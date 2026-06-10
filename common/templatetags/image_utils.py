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
        webp_src = f"{base_path}/processed.webp"

        img_tag = f'{start_tag}{webp_src}" data-zoomable data-zoom-src="{raw_src}" loading="lazy"'

        picture_tag = f"""<picture>
            <source srcset="{avif_src}" type="image/avif">
            <source srcset="{webp_src}" type="image/webp">
            {img_tag}
        </picture>"""

        return picture_tag

    content = re.sub(img_pattern, img_replacer, content, flags=re.IGNORECASE)

    video_pattern = r'<video[^>]*>[\s\S]*?src=["\']([^"\']*?/raw\.(?:mp4|webm|ogg|mov|avi|mkv))["\'][\s\S]*?</video>'
    
    def video_replacer(match):
        raw_src = match.group(1)
        base_path = raw_src.rsplit('/', 1)[0]
        
        webm_src = f"{base_path}/processed.webm"
        mp4_src = f"{base_path}/processed.mp4"

        return f"""
        <div class="video-container position-relative my-4" style="width: 100%;">
            <video autoplay loop muted playsinline class="w-100 rounded-4 shadow-sm" style="background-color: #1E1E1E;">
                <source src="{webm_src}" type="video/webm; codecs=av1">
                <source src="{mp4_src}" type="video/mp4">
                Seu navegador não suporta a tag de vídeo HTML5.
            </video>
            
            <div class="position-absolute d-flex gap-2" style="bottom: 16px; right: 16px; z-index: 10;">
                
                <button type="button" class="btn btn-sm btn-dark rounded-pill border border-secondary shadow d-flex align-items-center justify-content-center" 
                        style="width: 36px; height: 36px; background-color: rgba(30,30,30,0.75); backdrop-filter: blur(4px); transition: all 0.2s ease;"
                        onmouseover="this.style.transform='scale(1.05)'; this.style.backgroundColor='rgba(30,30,30,1)';"
                        onmouseout="this.style.transform='scale(1)'; this.style.backgroundColor='rgba(30,30,30,0.75)';"
                        onclick="const v = this.closest('.video-container').querySelector('video'); v.muted = !v.muted; this.querySelector('i').className = v.muted ? 'fa-solid fa-volume-xmark text-light' : 'fa-solid fa-volume-high text-light';"
                        title="Ligar/Desligar Som">
                    <i class="fa-solid fa-volume-xmark text-light"></i>
                </button>

                <a href="{raw_src}" target="_blank" rel="noopener noreferrer" 
                   class="text-decoration-none btn btn-sm btn-dark rounded-pill border border-secondary shadow d-flex align-items-center gap-2" 
                   style="background-color: rgba(30,30,30,0.75); backdrop-filter: blur(4px); transition: all 0.2s ease;"
                   onmouseover="this.style.transform='scale(1.05)'; this.style.backgroundColor='rgba(30,30,30,1)';"
                   onmouseout="this.style.transform='scale(1)'; this.style.backgroundColor='rgba(30,30,30,0.75)';"
                   title="Ver vídeo original (Alta Qualidade)">
                    <i class="fa-solid fa-expand text-light"></i> <span class="text-light" style="font-size: 0.8rem; font-weight: 600;">RAW</span>
                </a>
                
            </div>
        </div>
        """

    content = re.sub(video_pattern, video_replacer, content, flags=re.IGNORECASE)

    return mark_safe(content)
