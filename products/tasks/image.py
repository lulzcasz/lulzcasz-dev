import os
from celery import shared_task
from common.utils.image import download_to_temp, process_and_save_image


@shared_task(bind=True)
def process_image(self, relative_path):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        vf_scale_crop = "scale=256:256:force_original_aspect_ratio=decrease,crop=trunc(iw/2)*2:trunc(ih/2)*2"
        
        product_versions = ['webp', 'avif']

        for ext in product_versions:
            final_path = os.path.join(directory, f'processed.{ext}')

            if ext == 'avif':
                args = [
                    '-threads', '1', 
                    '-c:v', 'libaom-av1', 
                    '-still-picture', '1',
                    '-crf', '4', 
                    '-cpu-used', '4',
                    '-vf', vf_scale_crop, 
                    '-pix_fmt', 'yuv420p'
                ]
            else:
                args = [
                    '-threads', '1', 
                    '-c:v', 'libwebp', 
                    '-q:v', '95',
                    '-vf', vf_scale_crop, 
                    '-pix_fmt', 'yuv420p'
                ]

            process_and_save_image(input_path, final_path, args)

    return f"Successfully processed product image for {relative_path}"
