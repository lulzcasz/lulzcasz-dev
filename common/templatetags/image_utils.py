import os
import re
from django import template
from django.core.files.storage import default_storage
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def variant(image_field, size):
    ext = 'webp' if size == 'og' else 'avif'
    
    return default_storage.url(f"{os.path.dirname(image_field.name)}/{size}.{ext}")

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

        return f'{start_tag}{avif_src}" data-zoom-src="{raw_src}" class="zoomable" onerror="this.onerror=null; this.src=\'{raw_src}\';"{end_tag}'

    optimized_html = re.sub(pattern, replacer, content, flags=re.IGNORECASE)
    return mark_safe(optimized_html)
