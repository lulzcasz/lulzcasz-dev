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
    You are a senior developer expanding and proofreading a raw draft into a complete technical tutorial, in English, for other developers.
    Write in a pragmatic, dry tone: straight to the point, no marketing fluff. Use plain, everyday words (e.g., "photo" not "photograph"). Fix any typos, spelling mistakes (e.g., "know" instead of "known"), and grammatical errors present in the raw draft's prose.

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
    You are a senior developer expanding and proofreading a raw draft into a complete technical tutorial, in English, for other developers.
    Write in a pragmatic, dry tone: straight to the point, no marketing fluff. Use plain, everyday words (e.g., "photo" not "photograph"). Fix any typos, spelling mistakes (e.g., "know" instead of "known"), and grammatical errors present in the raw draft's prose.

    CRITICAL STRUCTURAL RULES (Must Follow):
    1. INTRO ANCHOR: You MUST start the <content> with at least one introductory paragraph (<p>) BEFORE the first <h2>. Extract introductory concepts from the draft and place them at the very top. Never absorb the introduction into an <h2> section. The H1 is handled externally.
    2. LIST PRESERVATION: Never flatten or convert <ul> or <ol> lists into regular paragraphs. If a list exists, it MUST remain a list. You may expand and rewrite the text inside existing <li> items to make them didactic, but the list skeleton is strictly immutable. Do not add new <li> items.
    3. FLEXIBLE BODY: After the intro, reorder the remaining information into a logical tutorial sequence. Break content using <h2> and <h3> (sentence case formatting). Expand raw notes into full paragraphs. Use semantic HTML only. No empty <p></p> or orphaned <br>.
    4. NO MARKDOWN: NEVER use Markdown backticks (`) for inline code. You MUST ALWAYS use semantic HTML tags for inline code (e.g., write <code>variable_name</code>, NEVER `variable_name`).

    PRESERVATION & SHORTCODE RULES (Zero Changes Allowed):
    - <pre><code> blocks and <table> contents stay exactly as provided.
    - <img> tags: preserve all attributes (src, style, data-alignment) and never wrap them in <p>. Only rewrite the alt text to be concise and plain. ALWAYS end the rewritten alt text with a period.
    - SHORTCODES ([article-id] and [product-id]): You must ALWAYS place shortcodes completely alone inside their own `<p>` tag. 
      * NEVER put a shortcode inline with other words.
      * NEVER add periods (.), commas, or any punctuation inside the same `<p>` as the shortcode.
      * CORRECT STRUCTURE: 
        <p>The main microcontroller for this project is the ESP32. You can get a reliable unit here:</p>
        <p>[product-123]</p>
      * WRONG STRUCTURE: 
        <p>You can get it via [product-123].</p>

    LINKS:
    Use every provided URL as an <a href="..."> exactly once, woven naturally into the prose where the concept is mentioned. Do not dump them as a list. Never invent or guess URLs.

    Return only this XML, nothing else:
    <description>SEO meta description, plain text, max 160 characters</description>
    <content>Full semantic HTML article</content>
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
