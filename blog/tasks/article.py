import logging
import os
import re
from functools import lru_cache
from pathlib import Path

from celery import shared_task
from google import genai
from google.genai import types
from pydantic import BaseModel

from ..models import Article

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

PROTECT_CODE_BLOCK_RE = re.compile(
    r'<pre\b([^>]*)>\s*<code\b([^>]*)>(.*?)</code>\s*</pre>',
    re.DOTALL | re.IGNORECASE,
)

RESTORE_CODE_BLOCK_RE = re.compile(
    r'(<pre\b[^>]*>\s*<code\b[^>]*\bdata-code-id="(\d+)"[^>]*>)(.*?)(</code>\s*</pre>)',
    re.DOTALL | re.IGNORECASE,
)


def protect_code_blocks(html):
    """Empty out every <pre><code>...</code></pre> block and tag it with a
    data-code-id attribute, keeping the original attributes. Models are far
    more reliable at leaving an already-empty tag (and its attributes) alone
    than at faithfully reproducing real code or even a text placeholder --
    there's nothing left to elide or paraphrase. Returns (protected_html,
    blocks) where blocks[i] is the original inner content of block i.
    """
    blocks = []

    def repl(match):
        idx = len(blocks)
        blocks.append(match.group(3))
        pre_attrs, code_attrs = match.group(1), match.group(2)
        return f'<pre{pre_attrs}><code{code_attrs} data-code-id="{idx}"></code></pre>'

    return PROTECT_CODE_BLOCK_RE.sub(repl, html), blocks


def restore_code_blocks(html, blocks):
    """Put the real code back wherever a data-code-id marker survived,
    regardless of whatever (if anything) the model left between the tags."""

    def repl(match):
        idx = int(match.group(2))
        original = blocks[idx] if idx < len(blocks) else match.group(3)
        return f"{match.group(1)}{original}{match.group(4)}"

    return RESTORE_CODE_BLOCK_RE.sub(repl, html)


def ensure_code_blocks_intact(html, blocks, task_name):
    """The data-code-id markers are how we find code blocks to restore --
    if the model dropped the marker/tag entirely, restoration silently does
    nothing and we'd save broken content. Detect that and fail loudly."""
    found = len(RESTORE_CODE_BLOCK_RE.findall(html))
    if found < len(blocks):
        raise RuntimeError(
            f"{task_name}: expected {len(blocks)} code block marker(s), found {found}"
        )

HUMANIZER_HTML_ADDENDUM = """
## How this applies here

The input is a semantic HTML article that is already structurally correct
(intro paragraph, <h2>/<h3> sections, lists, tables, code blocks, images,
shortcodes). Rewrite only the prose text nodes for AI patterns. Do not touch:

- <pre><code> blocks and <table> contents (character for character). A <pre><code> block may arrive empty with a data-code-id="N" attribute instead of real code -- that's expected: leave it as an empty tag with that attribute untouched, don't add text inside it.
- <img> tag attributes (only touch the alt text if it still reads like AI;
  keep it plain and ending in a period).
- Shortcodes ([article-id], [product-id]): keep them alone in their own <p>,
  no inline punctuation.
- Existing <a href="..."> links: keep the exact same hrefs and anchor
  placement.

Do not add, remove, or reorder any HTML element. Same tags, same nesting,
same order -- only the wording changes.

This is embedded mode: return only the final rewritten text, no draft, no
pattern list, no commentary.

Return description and content as JSON matching the schema.
"""


class ArticleOutput(BaseModel):
    description: str
    content: str


class TranslationOutput(BaseModel):
    description_pt: str
    content_pt: str


@lru_cache(maxsize=None)
def load_prompt(filename):
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


def ensure_complete(response, task_name):
    """Raise if the model stopped before finishing (truncation, safety,
    recitation, etc). Never let a partial response be treated as success."""
    candidates = getattr(response, "candidates", None) or []
    finish_reason = candidates[0].finish_reason if candidates else None
    reason_name = getattr(finish_reason, "name", str(finish_reason))
    if finish_reason is not None and reason_name != "STOP":
        raise RuntimeError(f"{task_name}: generation stopped early ({reason_name})")
    return response


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
    protected_draft, code_blocks = protect_code_blocks(base_html)

    section_name = article.section.safe_translation_getter('name', language_code='en') if article.section else "No section"
    category_name = article.category.safe_translation_getter('name', language_code='en') if article.category else "No category"
    tags_list = ", ".join([tag.safe_translation_getter('name', language_code='en') or "" for tag in article.tags.all()])

    system_prompt = load_prompt("article-generation.md")

    user_content = f"Title: {article.title}\nSection: {section_name}\nCategory: {category_name}\nTags: {tags_list}\n\nRough Draft (Expand the ideas into well-written paragraphs in English, but preserve the exact codes, tables, and images):\n{protected_draft}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
            max_output_tokens=8192,
        )
    )
    ensure_complete(response, "generate_full_article_task")

    raw_text = response.text
    logger.info(
        "generate_full_article_task article=%s draft_len=%d raw_response_len=%d",
        article_id, len(base_html), len(raw_text),
    )

    def extract_tag(tag, text):
        match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
        return match.group(1).strip() if match else ""

    desc_en = extract_tag("description", raw_text)
    cont_en = extract_tag("content", raw_text)
    ensure_code_blocks_intact(cont_en, code_blocks, "generate_full_article_task")
    cont_en = restore_code_blocks(cont_en, code_blocks)
    logger.info(
        "generate_full_article_task article=%s desc_len=%d content_len=%d",
        article_id, len(desc_en), len(cont_en),
    )

    if cont_en:
        article.set_current_language('en')
        article.content = cont_en
        article.description = desc_en
        article.save()

        humanize_article_task.delay(article.pk)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={'max_retries': 3},
    rate_limit='12/m'
)
def humanize_article_task(article_id):
    article = Article.objects.get(pk=article_id)

    en_content = article.safe_translation_getter('content', language_code='en') or ""
    en_description = article.safe_translation_getter('description', language_code='en') or ""

    if not en_content:
        return

    client = genai.Client()
    protected_content, code_blocks = protect_code_blocks(en_content)

    system_prompt = load_prompt("humanizer.md") + "\n\n" + HUMANIZER_HTML_ADDENDUM

    user_content = f"Meta Description (EN):\n{en_description}\n\nContent (EN, semantic HTML):\n{protected_content}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
            max_output_tokens=8192,
            response_mime_type="application/json",
            response_json_schema=ArticleOutput.model_json_schema(),
        )
    )
    ensure_complete(response, "humanize_article_task")

    data = ArticleOutput.model_validate_json(response.text)
    if data.content and code_blocks:
        ensure_code_blocks_intact(data.content, code_blocks, "humanize_article_task")
    restored_content = restore_code_blocks(data.content, code_blocks) if data.content else data.content

    if restored_content:
        article.set_current_language('en')
        article.content = restored_content
        article.description = data.description or en_description
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
    protected_content, code_blocks = protect_code_blocks(en_content)

    system_prompt = load_prompt("translation.md")

    user_content = f"Meta Description (EN):\n{en_description}\n\nConteúdo HTML (EN):\n{protected_content}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            max_output_tokens=8192,
            response_mime_type="application/json",
            response_json_schema=TranslationOutput.model_json_schema(),
        )
    )
    ensure_complete(response, "translate_en_to_pt_task")

    data = TranslationOutput.model_validate_json(response.text)
    if code_blocks:
        ensure_code_blocks_intact(data.content_pt, code_blocks, "translate_en_to_pt_task")

    article.set_current_language('pt-br')
    article.content = restore_code_blocks(data.content_pt, code_blocks)
    article.description = data.description_pt
    article.save()
