import os
import re
from celery import shared_task
from google import genai
from google.genai import types
from pydantic import BaseModel
from ..models import Article


class TranslationOutput(BaseModel):
    description_pt: str
    content_pt: str


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={'max_retries': 3},
    rate_limit='12/m'
)
def generate_full_article_task(article_id):
    article = Article.objects.get(pk=article_id)

    client = genai.Client()
    base_html = article.draft or ""

    section_name = article.section.safe_translation_getter('name', language_code='en') if article.section else "No section"
    category_name = article.category.safe_translation_getter('name', language_code='en') if article.category else "No category"
    tags_list = ", ".join([tag.safe_translation_getter('name', language_code='en') or "" for tag in article.tags.all()])

    system_prompt = """
    You are a senior developer expanding a raw draft into a complete technical tutorial, in English, for other developers.
    Write in a pragmatic, dry tone: straight to the point, no marketing fluff. Use plain, everyday words (e.g., "photo" not "photograph").

    CRITICAL STRUCTURAL RULES (Must Follow):
    1. INTRO ANCHOR: You MUST start the <content> with at least one introductory paragraph (<p>) BEFORE the first <h2>. Extract introductory concepts from the draft and place them at the very top. Never absorb the introduction into an <h2> section. The H1 is handled externally.
    2. LIST PRESERVATION: Never flatten or convert <ul> or <ol> lists into regular paragraphs. If a list exists, it MUST remain a list. You may expand and rewrite the text inside existing <li> items to make them didactic, but the list skeleton is strictly immutable. Do not add new <li> items.
    3. FLEXIBLE BODY: After the intro, reorder the remaining information into a logical tutorial sequence. Break content using <h2> and <h3> (sentence case formatting). Expand raw notes into full paragraphs. Use semantic HTML only. No empty <p></p> or orphaned <br>.

    PRESERVATION RULES (Zero Changes Allowed):
    - <pre><code> blocks and <table> contents stay exactly as provided.
    - <img> tags: preserve all attributes (src, style, data-alignment) and never wrap them in <p>. Only rewrite the alt text to be concise and plain. ALWAYS end the rewritten alt text with a period.
    - [article-id] shortcode: renders a related article card. Write a natural 1-2 sentence lead-in before it explaining its relevance. Never wrap the shortcode itself in <p> or inline text.
    - [product-id] shortcode: renders buy buttons. The sentence immediately before it MUST name the product and its purpose. Never wrap the shortcode in <p>.

    LINKS:
    Use every provided URL as an <a href="..."> exactly once, woven naturally into the prose where the concept is mentioned. Do not dump them as a list. Never invent or guess URLs.

    Return only this XML, nothing else:
    <description>SEO meta description, plain text, max 160 characters</description>
    <content>Full semantic HTML article</content>
    """

    user_content = f"Title: {article.title}\nSection: {section_name}\nCategory: {category_name}\nTags: {tags_list}\n\nRough Draft (Expand the ideas into well-written paragraphs in English, but preserve the exact codes, tables, and images):\n{base_html}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
        )
    )

    raw_text = response.text

    def extract_tag(tag, text):
        match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
        return match.group(1).strip() if match else ""

    desc_en = extract_tag("description", raw_text)
    cont_en = extract_tag("content", raw_text)

    if cont_en:
        article.set_current_language('en')
        article.content = cont_en
        article.description = desc_en
        article.save()

        translate_en_to_pt_task.delay(article.pk)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={'max_retries': 3}
)
def translate_en_to_pt_task(article_id):
    article = Article.objects.get(pk=article_id)

    en_content = article.safe_translation_getter('content', language_code='en') or ""
    en_description = article.safe_translation_getter('description', language_code='en') or ""

    if not en_content or not en_description:
        return

    client = genai.Client()

    system_prompt = """
    You are a specialized technical translator, English to Brazilian Portuguese, translating dev-to-dev content.

    This is a literal, structure-preserving translation, NOT a rewrite. You are translating text nodes only — the HTML skeleton must come out identical to the source: same tags, same nesting, same number of elements, same order. Concretely:
    - Do not add, remove, merge, or split any element — no new headings, paragraphs, sentences, list items, or images that aren't in the source, and none of the source's removed either.
    - Do not turn paragraphs into lists, or lists into paragraphs, or otherwise change the structure around the text.
    - Do not add examples, clarifications, or extra detail that isn't a direct translation of something already in the source — if the English doesn't say it, the Portuguese doesn't either.
    - <pre><code> blocks are copied character for character, with zero translation — including comments and strings inside the code.
    If you're unsure whether to add something, don't.

    Translate like a Brazilian developer writing to another developer — plain, everyday words, no formal/literary vocabulary (e.g. "foto" not "fotografia", "imagem" not "representação visual"). Keep the pragmatic, dry tone of the original; don't make it sound more formal in Portuguese than it is in English.

    content_pt: translate the prose, but keep all HTML tags, attributes, classes, URLs, tables, and <pre><code> blocks exactly as in the source. Never wrap <img> tags in <p>. Headings (<h2>, <h3>) are prose too — their text MUST be translated to Portuguese like everything else, just keep using sentence case formatting for them (only first word and proper nouns capitalized) after translating. A heading left in English is a translation failure, same as a paragraph left in English. Exception: translate the text inside each <img>'s `alt` attribute to Portuguese — every other attribute (src, style, data-alignment, etc.) stays untouched.

    description_pt: translate keeping its SEO appeal, plain text, max 160 characters.
    """

    user_content = f"Meta Description (EN):\n{en_description}\n\nConteúdo HTML (EN):\n{en_content}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            response_mime_type="application/json",
            response_json_schema=TranslationOutput.model_json_schema(),
        )
    )

    data = TranslationOutput.model_validate_json(response.text)

    article.set_current_language('pt-br')
    article.content = data.content_pt
    article.description = data.description_pt
    article.save()
