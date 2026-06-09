import os
from celery import shared_task
from common.utils.image import download_to_temp, process_and_save_image

@shared_task(bind=True)
def process_image(self, relative_path, kind):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if kind == 'cover':
            versions = [
                {'size': 'large',  'ext': 'webp', 'w': 1200, 'h': 630, 'args': ['-threads', '2', '-c:v', 'libwebp', '-q:v', '80']},
                {'size': 'medium', 'ext': 'webp', 'w': 960,  'h': 504, 'args': ['-threads', '2', '-c:v', 'libwebp', '-q:v', '85']},
                {'size': 'small',  'ext': 'webp', 'w': 480,  'h': 252, 'args': ['-threads', '2', '-c:v', 'libwebp', '-q:v', '92']},
                {'size': 'large',  'ext': 'avif', 'w': 1200, 'h': 630, 'args': ['-threads', '2', '-c:v', 'libaom-av1', '-still-picture', '1', '-cpu-used', '6', '-crf', '24']},
                {'size': 'medium', 'ext': 'avif', 'w': 960,  'h': 504, 'args': ['-threads', '2', '-c:v', 'libaom-av1', '-still-picture', '1', '-cpu-used', '6', '-crf', '16']},
                {'size': 'small',  'ext': 'avif', 'w': 480,  'h': 252, 'args': ['-threads', '2', '-c:v', 'libaom-av1', '-still-picture', '1', '-cpu-used', '6', '-crf', '8']},
            ]
            
            for config in versions:
                final_path = os.path.join(directory, f"{config['size']}.{config['ext']}")

                vf_scale_crop = f"scale={config['w']}:{config['h']}:force_original_aspect_ratio=increase,crop={config['w']}:{config['h']}"
                
                args = ['-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'] + config['args']
                
                process_and_save_image(input_path, final_path, args)

        elif kind == 'content_image':
            vf_scale_crop = "scale='min(960,iw)':'min(620,ih)':force_original_aspect_ratio=decrease,crop=trunc(iw/2)*2:trunc(ih/2)*2"

            content_versions = ['webp', 'avif']

            for ext in content_versions:
                final_path = os.path.join(directory, f'processed.{ext}')

                if ext == 'avif':
                    args = [
                        '-threads', '2', '-c:v', 'libaom-av1', '-still-picture', '1', 
                        '-crf', '16', '-cpu-used', '6',
                        '-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'
                    ]
                else: # webp
                    args = [
                        '-threads', '2', '-c:v', 'libwebp', '-q:v', '85',
                        '-vf', vf_scale_crop, '-pix_fmt', 'yuv420p'
                    ]
                
                process_and_save_image(input_path, final_path, args)

    return f"Successfully processed {kind} for {relative_path}"
