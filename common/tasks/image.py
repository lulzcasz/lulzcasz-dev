import os
from celery import shared_task
from PIL import Image
from common.utils.image import download_to_temp, process_and_save_image

@shared_task(bind=True)
def process_image(self, relative_path, kind):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if kind == 'cover':
            versions = [
                {'size': 'large',  'ext': 'avif', 'w': 1200, 'h': 630, 'args': ['-threads', '1', '-c:v', 'libaom-av1', '-still-picture', '1', '-crf', '24']},
                {'size': 'large',  'ext': 'webp', 'w': 1200, 'h': 630, 'args': ['-threads', '1', '-c:v', 'libwebp', '-q:v', '80']},
                {'size': 'medium', 'ext': 'avif', 'w': 960,  'h': 504, 'args': ['-threads', '1', '-c:v', 'libaom-av1', '-still-picture', '1', '-crf', '16']},
                {'size': 'medium', 'ext': 'webp', 'w': 960,  'h': 504, 'args': ['-threads', '1', '-c:v', 'libwebp', '-q:v', '85']},
                {'size': 'small',  'ext': 'avif', 'w': 480,  'h': 252, 'args': ['-threads', '1', '-c:v', 'libaom-av1', '-still-picture', '1', '-crf', '8']},
                {'size': 'small',  'ext': 'webp', 'w': 480,  'h': 252, 'args': ['-threads', '1', '-c:v', 'libwebp', '-q:v', '92']},
            ]
            
            for config in versions:
                final_path = os.path.join(directory, f"{config['size']}.{config['ext']}")

                vf_scale_crop = f"scale={config['w']}:{config['h']}:force_original_aspect_ratio=increase,crop={config['w']}:{config['h']}"
                
                args = ['-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'] + config['args']
                
                process_and_save_image(input_path, final_path, args)

        elif kind == 'content_image':
            with Image.open(input_path) as img:
                is_animated = getattr(img, 'is_animated', False)

            vf_scale_crop = "fps=15,scale='min(960,iw)':'min(620,ih)':force_original_aspect_ratio=decrease,crop=trunc(iw/2)*2:trunc(ih/2)*2"

            content_versions = ['avif', 'webp']

            for ext in content_versions:
                final_path = os.path.join(directory, f'processed.{ext}')

                if is_animated:
                    if ext == 'avif':
                        args = [
                            '-threads', '1', '-c:v', 'libsvtav1', '-crf', '38', '-preset', '8',
                            '-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'
                        ]
                    else:
                        args = [
                            '-threads', '1', '-c:v', 'libwebp', '-loop', '0', '-q:v', '70',
                            '-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'
                        ]
                else:
                    if ext == 'avif':
                        args = [
                            '-threads', '1', '-c:v', 'libaom-av1', '-still-picture', '1', '-crf', '16', '-cpu-used', '4',
                            '-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'
                        ]
                    else:
                        args = [
                            '-threads', '1', '-c:v', 'libwebp', '-q:v', '85',
                            '-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'
                        ]
                
                process_and_save_image(input_path, final_path, args)

    return f"Successfully processed {kind} for {relative_path}"
