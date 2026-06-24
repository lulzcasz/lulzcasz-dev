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

    img_pattern = r'(<img[^>]*?src=["\'])([^"\']*?/raw\.(?:jpg|jpeg|png|gif|webp|avif))(["\'][^>]*?>)'
    
    def img_replacer(match):
        start_tag = match.group(1)
        raw_src = match.group(2)
        end_tag = match.group(3)

        base_path = raw_src.rsplit('/', 1)[0]
        avif_src = f"{base_path}/processed.avif"

        tag_without_close = f'{start_tag}{raw_src}{end_tag}'.rstrip('>').rstrip('/')
        img_tag = f'{tag_without_close} data-zoomable data-zoom-src="{raw_src}" loading="lazy">'

        picture_tag = f"""<picture>
            <source srcset="{avif_src}" type="image/avif">
            {img_tag}
        </picture>"""
        
        return picture_tag

    content = re.sub(img_pattern, img_replacer, content, flags=re.IGNORECASE)

    video_pattern = r'<video([^>]*)>[\s\S]*?src=["\']([^"\']*?/raw\.(?:mp4|webm|ogg|mov|avi|mkv))["\'][\s\S]*?</video>'
    
    def video_replacer(match):
        video_attributes = match.group(1)
        raw_src = match.group(2)
        base_path = raw_src.rsplit('/', 1)[0]
        
        webm_src = f"{base_path}/processed.webm"

        width_match = re.search(r'width=["\'](\d+)(?:px)?["\']', video_attributes, re.IGNORECASE)
        width_val = int(width_match.group(1)) if width_match else None
        
        if not width_val:
            style_width = re.search(r'width:\s*(\d+)px', video_attributes, re.IGNORECASE)
            if style_width:
                width_val = int(style_width.group(1))

        if width_val:
            max_allowed_width = min(width_val, 960)
            container_style = f"width: 100%; max-width: {max_allowed_width}px;"
        else:
            container_style = "width: 100%; max-width: 960px;"

        return f"""
        <div class="relative my-4 mx-auto" style="{container_style}">
            <video autoplay loop muted playsinline class="w-full h-auto rounded-xl shadow-sm" style="background-color: #1E1E1E;">
                <source src="{webm_src}" type="video/webm; codecs=av1">
                <source src="{raw_src}" type="video/mp4">
                Seu navegador não suporta a tag de vídeo HTML5.
            </video>
            
            <div class="absolute flex gap-2" style="bottom: 16px; right: 16px; z-index: 10;">
                
                <button type="button" class="rounded-full border border-gray-600 shadow flex items-center justify-center text-white cursor-pointer" 
                        style="width: 36px; height: 36px; background-color: rgba(30,30,30,0.75); backdrop-filter: blur(4px); transition: all 0.2s ease;"
                        onmouseover="this.style.transform='scale(1.05)'; this.style.backgroundColor='rgba(30,30,30,1)';"
                        onmouseout="this.style.transform='scale(1)'; this.style.backgroundColor='rgba(30,30,30,0.75)';"
                        onclick="const v = this.closest('div.relative').querySelector('video'); v.muted = !v.muted; this.querySelector('i').className = v.muted ? 'fa-solid fa-volume-xmark text-white' : 'fa-solid fa-volume-high text-white';"
                        title="Ligar/Desligar Som">
                    <i class="fa-solid fa-volume-xmark text-white"></i>
                </button>

                <a href="{raw_src}" target="_blank" rel="noopener noreferrer" 
                   class="no-underline rounded-full border border-gray-600 shadow flex items-center gap-2 px-3 text-white" 
                   style="height: 36px; background-color: rgba(30,30,30,0.75); backdrop-filter: blur(4px); transition: all 0.2s ease;"
                   onmouseover="this.style.transform='scale(1.05)'; this.style.backgroundColor='rgba(30,30,30,1)';"
                   onmouseout="this.style.transform='scale(1)'; this.style.backgroundColor='rgba(30,30,30,0.75)';"
                   title="Ver vídeo original (Alta Qualidade)">
                    <i class="fa-solid fa-expand text-white"></i> <span class="text-white" style="font-size: 0.8rem; font-weight: 600;">RAW</span>
                </a>
                
            </div>
        </div>
        """

    content = re.sub(video_pattern, video_replacer, content, flags=re.IGNORECASE)

    return mark_safe(content)
