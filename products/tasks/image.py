import os
from celery import shared_task
from common.utils.image import download_to_temp, process_and_save_image


@shared_task(bind=True)
def process_image(self, relative_path):
    directory = os.path.dirname(relative_path)
    final_path = os.path.join(directory, 'processed.avif')

    args = [
        '-threads', '1',
        '-vf', "scale=512:512:force_original_aspect_ratio=decrease",
        '-c:v', 'libaom-av1',
        '-still-picture', '1',
        '-crf', '25', 
        '-cpu-used', '4',
        '-pix_fmt', 'yuv420p' 
        ]

    with download_to_temp(relative_path) as input_path:
        process_and_save_image(input_path, final_path, args)

    return f"Successfully processed product image for {relative_path}"
