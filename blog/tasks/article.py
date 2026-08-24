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

    Write in a pragmatic, dry tone: straight to the point, no marketing fluff, no cheesy transitions. Use plain, everyday words — the way a dev explains something to another dev in a README or a Slack message, not like an encyclopedia entry. Avoid formal/literary vocabulary (e.g. say "photo" or "screenshot", not "photograph"; say "picture", not "visual representation"). If a simpler, more common word exists, use it. Expand every section into full, didactic paragraphs that explain the concepts, wiring, and code — never leave notes unexplained or paragraphs empty.

    Formatting:
    - Semantic HTML only (<h2>, <h3>, <p>, <ul>, <ol>, <pre><code>, <table>, <img>). No empty <p></p> or orphaned <br>.
    - Headings in sentence case (only first word and proper nouns capitalized).
    - You may add better explanations inside existing <li> items, but never add new <li> items.
    - The article title is rendered separately as the H1. Start the content directly with the introduction paragraph(s) — do NOT add a heading (like "Introduction") before it. The first <h2> only appears when the first real section begins.
    - You're free to reorder the draft's information into whatever sequence reads best as a tutorial — the draft's order is raw notes, not a fixed outline. Break content into <h2> and <h3> sections as often as makes sense; don't force everything under one heading or leave long unstructured stretches just because the draft wasn't split that way.

    Preserve exactly as given, with zero changes: <pre><code> blocks, <table> contents, <img> tags (including every attribute like data-alignment, style, src — never wrap them in <p>).

    Image alt text: in the draft, each <img>'s `alt` attribute already contains a rough, informally written description of what the image shows. Read that raw alt text and rewrite it into a proper, concise `alt` attribute using plain, everyday words (e.g. "photo", "screenshot", "diagram" — not "photograph" or "visual representation"). Every other attribute (src, style, data-alignment, etc.) stays untouched. If it helps the reader, you may also add a short sentence before or after the image describing what it shows — but this is optional, not mandatory.

    Shortcodes (preserve each one exactly, character for character — never alter, wrap in <p>, or move them from their position):
    - [article-id]: renders as a block-level card (cover image, title, description) linking to another article. Never wrap it in <p> or inline text around it. Write a natural one or two sentence lead-in before it explaining why the reader might want to check that reference out — never just copy a raw draft label like "MicroPython implementation:" verbatim.
    - [product-id]: renders as a horizontal row of marketplace buttons to buy an item — it shows NO product name or description, only the buttons. Since the shortcode itself won't tell the reader what they're buying, the sentence right before it MUST name the product and briefly say what it's for, so the buttons aren't floating with zero context.

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
            temperature=0.8,
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

    Translate like a Brazilian developer writing to another developer — plain, everyday words, no formal/literary vocabulary (e.g. "foto" not "fotografia", "imagem" not "representação visual"). Keep the pragmatic, dry tone of the original; don't make it sound more formal in Portuguese than it is in English.

    content_pt: translate the prose, but keep all HTML tags, attributes, classes, URLs, tables, and <pre><code> blocks exactly as in the source. Never wrap <img> tags in <p>. Keep <h2>/<h3> headings in sentence case. Exception: translate the text inside each <img>'s `alt` attribute to Portuguese — every other attribute (src, style, data-alignment, etc.) stays untouched.

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
