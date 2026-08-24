import os
from celery import shared_task
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel
from ..models import Article


class FullArticleOutput(BaseModel):
    description_en: str
    content_en: str
    description_pt: str
    content_pt: str


class TranslationOutput(BaseModel):
    description_pt: str
    content_pt: str


import os
import re
from celery import shared_task
from google import genai
from google.genai import types
from google.genai.errors import APIError
from ..models import Article


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

    section_name = article.section.safe_translation_getter('name', language_code='en') if article.section else "Sem seção"
    category_name = article.category.safe_translation_getter('name', language_code='en') if article.category else "Sem categoria"
    tags_list = ", ".join([tag.safe_translation_getter('name', language_code='en') or "" for tag in article.tags.all()])

    system_prompt = """
    You are a senior technical writer writing from developer to developer (dev-to-dev style). Keep the tone direct, practical, and objective, avoiding pompous language or deep explanations unless explicitly requested by the user.
    Expand the provided HTML skeleton and user instructions into a complete article in ENGLISH (_en) and its translation into BRAZILIAN PORTUGUESE (_pt).

    You MUST return your response strictly using the following XML tags:
    <description_en>SEO meta description (max 160 chars, plain text)</description_en>
    <content_en>Full semantic HTML for Tiptap with preserved codes</content_en>
    <description_pt>SEO meta description in PT-BR (max 160 chars, plain text)</description_pt>
    <content_pt>Full semantic HTML translated to PT-BR with preserved codes</content_pt>

    Rules:
    1. CONTEXT: Use the provided Title, Section, Category, and Tags as context to guide the tone and focus.
    2. CONTENT: Output must be strictly semantic HTML for Tiptap (<h2>, <h3>, <p>, <ul>, <ol>, <pre><code>, <table>, <img>). DO NOT use <html>, <body>, or <head>.
    - PRESERVE 100% of all provided <pre><code>, <table>, <img>, and shortcode tags ([product-id], [article-id]) exactly as they are. DO NOT remove, empty, or alter code contents.
    - NEVER add comments, documentation, explanations, or modifications inside any provided code snippets or terminal commands (<pre><code>); keep all code and commands 100% identical and untouched.
    - You are allowed to intelligently reorganize the flow and use <h2> and <h3> headings.
    - The opening introductory paragraph immediately following the main title must be a clean <p> tag without any preceding <h2> heading.
    - All <h2> and <h3> headings must use sentence case (capitalize only the first word and proper nouns).
    - All <img> tags must be centered by wrapping them in <p style="text-align: center"> ... </p>.
    3. SUMMARY: Write an SEO-focused meta description with a MAXIMUM of 160 characters. Plain text only, no HTML tags.
    """

    user_content = f"Title: {article.title}\nSection: {section_name}\nCategory: {category_name}\nTags: {tags_list}\n\nHTML Base Skeleton (Keep this HTML entirely, preserving every <pre><code> tag, tables, images, and shortcodes):\n{base_html}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
        )
    )

    raw_text = response.text

    def extract_tag(tag, text):
        match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
        return match.group(1).strip() if match else ""

    desc_en = extract_tag("description_en", raw_text)
    cont_en = extract_tag("content_en", raw_text)
    desc_pt = extract_tag("description_pt", raw_text)
    cont_pt = extract_tag("content_pt", raw_text)

    if cont_en:
        article.set_current_language('en')
        article.content = cont_en
        article.description = desc_en
        article.save()

    if cont_pt:
        article.set_current_language('pt-br')
        article.content = cont_pt
        article.description = desc_pt
        article.save()


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
    1. CONTENT (content_pt): Keep ALL HTML tags, attributes, classes, URLs, tables, and <pre><code> code blocks EXACTLY the same, including any <p style="text-align: center"> wrapper around <img> tags. All <h2> and <h3> headings must use sentence case in the translation as well (capitalize only the first word and proper nouns).
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
