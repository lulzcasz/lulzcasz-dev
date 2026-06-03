import os
from celery import shared_task
from PIL import Image
from common.utils.image import download_to_temp, process_and_save_image

@shared_task(bind=True)
def process_image(self, relative_path, kind):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if kind == 'cover':
            versions = {
                'display': {'w': 960, 'h': 502, 'ext': 'avif', 'args': ['-threads', '1', '-c:v', 'libaom-av1', '-still-picture', '1', '-crf', '16']},
                'thumbnail': {'w': 480, 'h': 252, 'ext': 'avif', 'args': ['-threads', '1', '-c:v', 'libaom-av1', '-still-picture', '1', '-crf', '8']},
                'og': {'w': 1200, 'h': 630, 'ext': 'webp', 'args': ['-threads', '1', '-c:v', 'libwebp', '-q:v', '80']}
            }
            
            for suffix, config in versions.items():
                final_path = os.path.join(directory, f"{suffix}.{config['ext']}")

                vf_scale_crop = f"scale={config['w']}:{config['h']}:force_original_aspect_ratio=increase,crop={config['w']}:{config['h']}"
                
                args = ['-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'] + config['args']
                
                process_and_save_image(input_path, final_path, args)

        elif kind == 'content_image':
            final_path = os.path.join(directory, 'processed.avif')
            
            with Image.open(input_path) as img:
                is_animated = getattr(img, 'is_animated', False)

            vf_scale_crop = "scale='min(960,iw)':'min(620,ih)':force_original_aspect_ratio=decrease,crop=trunc(iw/2)*2:trunc(ih/2)*2"

            if is_animated:
                args = [
                    '-threads', '1',
                    '-c:v', 'libsvtav1', '-crf', '38', '-preset', '8',
                    '-vf', vf_scale_crop,
                    '-pix_fmt', 'yuv420p'
                ]
            else:
                args = [
                    '-threads', '1',
                    '-vf', vf_scale_crop,
                    '-pix_fmt', 'yuv420p', '-c:v', 'libaom-av1',
                    '-still-picture', '1', '-crf', '10', '-cpu-used', '4'
                ]
            
            process_and_save_image(input_path, final_path, args)

    return f"Successfully processed {kind} for {relative_path}"
