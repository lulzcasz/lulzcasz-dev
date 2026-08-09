import os
from celery import shared_task
from blog.utils.image import download_to_temp, process_and_save_image

@shared_task(bind=True)
def process_video(self, relative_path, section):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if section == 'content_video':
            vf_raw = "hqdn3d=2:1.5:3:2.2,fps=30,scale='min(1920,iw)':-2"
            path_raw = os.path.join(directory, 'raw.webm')
            
            args_raw = [
                '-threads', '4', 
                '-c:v', 'libsvtav1',
                '-preset', '7',
                '-crf', '26',
                '-an',
                '-vf', vf_raw,
                '-pix_fmt', 'yuv420p'
            ]
            process_and_save_image(input_path, path_raw, args_raw)

            vf_inline = "hqdn3d=2:1.5:3:2.2,fps=30,scale='min(960,iw)':-2"
            path_inline = os.path.join(directory, 'processed.webm')

            args_inline = [
                '-threads', '4',
                '-c:v', 'libsvtav1',
                '-preset', '8',
                '-crf', '42',
                '-an',
                '-vf', vf_inline,
                '-pix_fmt', 'yuv420p'
            ]
            process_and_save_image(input_path, path_inline, args_inline)

    return f"Successfully processed {section} for {relative_path}"
