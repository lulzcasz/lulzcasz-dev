import os
from celery import shared_task
from blog.utils.image import download_to_temp, process_and_save_image

@shared_task(bind=True)
def process_video(self, relative_path, section):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if section == 'content_video':
            vf_inline = "hqdn3d=2:1.5:3:2.2,fps=30,scale='min(1920,iw)':-2"
            path_inline = os.path.join(directory, 'processed.webm')

            args_inline = [
                '-threads', '4',
                '-c:v', 'libsvtav1',
                '-preset', '5',     
                '-crf', '34',       
                '-an',              
                '-vf', vf_inline,
                '-pix_fmt', 'yuv420p'
            ]
            process_and_save_image(input_path, path_inline, args_inline)

            path_poster = os.path.join(directory, 'poster.avif')
            
            args_poster = [
                '-vframes', '1',        
                '-threads', '2',
                '-c:v', 'libaom-av1',
                '-still-picture', '1',
                '-crf', '26',
                '-cpu-used', '6',
                '-vf', "scale='min(1920,iw)':-2",
                '-pix_fmt', 'yuv420p'
            ]
            process_and_save_image(input_path, path_poster, args_poster)

    return f"Successfully processed {section} for {relative_path}"
