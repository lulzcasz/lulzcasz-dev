import os
import re
from django import template
from django.core.files.storage import default_storage
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def variant(image_field, filename):
    if not image_field:
        return ""

    return default_storage.url(f"{os.path.dirname(image_field.name)}/{filename}")

@register.filter
def optimize_content_images(content):
    if not content:
        return content

    pattern = r'(<img[^>]*?src=["\'])([^"\']*?/raw\.[a-zA-Z0-9]+)(["\'][^>]*?>)'
    
    def replacer(match):
        start_tag = match.group(1)
        raw_src = match.group(2)
        end_tag = match.group(3)

        base_path = raw_src.rsplit('/', 1)[0]
        avif_src = f"{base_path}/processed.avif"
        webp_src = f"{base_path}/processed.webp"

        img_tag = f'{start_tag}{webp_src}" data-zoom-src="{raw_src}" class="zoomable" loading="lazy" onerror="this.onerror=null; this.src=\'{raw_src}\';"{end_tag}'

        picture_tag = f"""<picture>
            <source srcset="{avif_src}" type="image/avif">
            <source srcset="{webp_src}" type="image/webp">
            {img_tag}
        </picture>"""

        return picture_tag

    optimized_html = re.sub(pattern, replacer, content, flags=re.IGNORECASE)
    return mark_safe(optimized_html)
