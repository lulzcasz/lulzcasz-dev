import os
from celery import shared_task
from common.utils.image import download_to_temp, process_and_save_image

@shared_task(bind=True)
def process_video(self, relative_path, kind):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if kind == 'content_video':
            vf_scale_crop = "fps=24,scale='min(960,iw)':'min(504,ih)':force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2"

            final_path = os.path.join(directory, 'processed.webm')

            args = [
                '-threads', '1',
                '-c:v', 'libaom-av1',
                '-crf', '32',
                '-b:v', '0',
                '-cpu-used', '4',
                '-c:a', 'libopus',
                '-b:a', '96k',
                '-vf', vf_scale_crop,
                '-pix_fmt', 'yuv420p'
            ]

            process_and_save_image(input_path, final_path, args)

    return f"Successfully processed {kind} for {relative_path}"
