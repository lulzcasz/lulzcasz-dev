import os
from celery import shared_task
from common.utils.image import download_to_temp, process_and_save_avif

@shared_task(bind=True)
def process_image(self, relative_path):
    directory = os.path.dirname(relative_path)
    final_path = os.path.join(directory, 'processed.avif')

    args = [
        '-vf', "crop='min(iw,ih)':'min(iw,ih)',scale=256:256",
        '-pix_fmt', 'yuv420p',
        '-c:v', 'libaom-av1',
        '-still-picture', '1',
        '-crf', '25',
        '-cpu-used', '4'
    ]

    with download_to_temp(relative_path) as input_path:
        process_and_save_avif(input_path, final_path, args)

    return f"Successfully processed avatar for {relative_path}"
