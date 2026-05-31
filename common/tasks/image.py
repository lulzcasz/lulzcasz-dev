import os
from celery import shared_task
from PIL import Image
from common.utils.image import download_to_temp, process_and_save_avif

@shared_task(bind=True)
def process_image(self, relative_path, kind):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if kind == 'cover':
            versions = {
                'small': (512, 288, 6),
                'medium': (896, 504, 10),
                'large': (1280, 720, 16),
            }
            for suffix, (width, height, crf) in versions.items():
                final_path = os.path.join(directory, f"{suffix}.avif")
                args = [
                    '-vf', f"scale='if(lt(iw/ih,{width}/{height}),{width},-2)':'if(lt(iw/ih,{width}/{height}),-2,{height})',crop={width}:{height}",
                    '-pix_fmt', 'yuv420p', '-c:v', 'libaom-av1', 
                    '-still-picture', '1', '-crf', str(crf)
                ]
                process_and_save_avif(input_path, final_path, args)

        elif kind == 'content_image':
            final_path = os.path.join(directory, 'processed.avif')
            
            with Image.open(input_path) as img:
                is_animated = getattr(img, 'is_animated', False)

            if is_animated:
                args = [
                    '-c:v', 'libsvtav1', '-crf', '38', '-preset', '8',
                    '-vf', "scale='min(1024,iw)':-2:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    '-pix_fmt', 'yuv420p'
                ]
            else:
                args = [
                    '-vf', "scale='min(1024,iw)':'min(576,ih)':force_original_aspect_ratio=decrease,crop=trunc(iw/2)*2:trunc(ih/2)*2:0:0",
                    '-pix_fmt', 'yuv420p', '-c:v', 'libaom-av1',
                    '-still-picture', '1', '-crf', '25', '-cpu-used', '4'
                ]
            
            process_and_save_avif(input_path, final_path, args)

    return f"Successfully processed {kind} for {relative_path}"
