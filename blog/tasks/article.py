import os
import re
from celery import shared_task
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel
from ..models import Article


class TranslationOutput(BaseModel):
    description_pt: str
    content_pt: str


@shared_task(
    autoretry_for=(APIError, Exception),
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
    You are a senior developer writing a technical blog post for other developers. Your job is to expand a raw skeleton draft into a complete, well-written article ONLY in ENGLISH.

    You MUST return your response strictly using the following XML tags:
    <description>SEO meta description (max 160 chars, plain text)</description>
    <content>Full semantic HTML for Tiptap with preserved codes</content>

    Rules for Generating the Content:
    1. EXPAND AND EXPLAIN: You MUST write complete paragraphs. Do not leave the text empty or just output the raw notes. Take the provided skeleton and explain the concepts, the hardware wiring, and the code clearly. Write enough text to make it a fully fleshed-out, didactic tutorial.
    2. TONE (PRAGMATIC AND DRY): Write like a senior engineer talking to another dev. Go straight to the point. NO marketing fluff, NO pompous language, NO cheesy transitions. Just state facts clearly (e.g., "Wire the components according to the table below:", "Fritzing diagram:", "Physical circuit on a breadboard:").
    3. HTML STRUCTURE & FORMATTING: Output strictly semantic HTML (<h2>, <h3>, <p>, <ul>, <ol>, <pre><code>, <table>, <img>).
    - NEVER output empty paragraphs (<p></p>), orphaned <br> tags, or extra spacing between text and images.
    - All <h2> and <h3> headings MUST use sentence case (capitalize only the first word and proper nouns).
    4. PRESERVE MEDIA & CODE (CRITICAL): You MUST PRESERVE 100% of all provided <pre><code>, <table>, <img>, and shortcodes (e.g., [product-id]).
    - DO NOT wrap <img> tags in <p> tags. Leave the <img> tags completely loose and exactly as they appear in the draft.
    - DO NOT alter, remove, or modify ANY attributes inside <img> tags. Keep `data-alignment`, `style`, and `src` EXACTLY as provided.
    - NEVER alter or explain inside code contents, URLs, or table data.
    5. LIST CONSTRAINT: If the draft contains a list (<ul> or <ol>), you may write better explanations inside the existing items, but you are STRICTLY FORBIDDEN from adding new list items (<li>).
    6. SUMMARY: Write an SEO-focused meta description with a MAXIMUM of 160 characters. Plain text only.
    """

    user_content = f"Title: {article.title}\nSection: {section_name}\nCategory: {category_name}\nTags: {tags_list}\n\nRough Draft (Expand the ideas into well-written paragraphs in English, but preserve the exact codes, tables, and images):\n{base_html}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,
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
    autoretry_for=(APIError, Exception),
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
    You are a specialized technical translator.
    Translate the HTML content and the meta description from English to Brazilian Portuguese.

    Critical Rules:
    1. CONTENT (content_pt): Keep ALL HTML tags, attributes, classes, URLs, tables, and <pre><code> code blocks EXACTLY the same.
    - DO NOT wrap <img> tags in <p> tags. Leave them exactly as they are formatted in the source HTML.
    - All <h2> and <h3> headings must use sentence case in the translation as well (capitalize only the first word and proper nouns).
    2. SUMMARY (description_pt): Translate the text while keeping its SEO appeal and the 160-character limit. Plain text only, no HTML.
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
