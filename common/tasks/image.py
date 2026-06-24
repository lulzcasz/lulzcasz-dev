import os
from celery import shared_task
from common.utils.image import download_to_temp, process_and_save_image

@shared_task(bind=True)
def process_image(self, relative_path, kind):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if kind == 'cover':
            versions = [
                {'size': 'large',  'ext': 'jpg',  'w': 1200, 'h': 630, 'q': '3'},
                {'size': 'medium', 'ext': 'avif', 'w': 960,  'h': 504, 'crf': '16'},
                {'size': 'small',  'ext': 'avif', 'w': 480,  'h': 252, 'crf': '10'},
            ]
            
            for config in versions:
                final_path = os.path.join(directory, f"{config['size']}.{config['ext']}")

                vf_scale_crop = f"scale={config['w']}:{config['h']}:force_original_aspect_ratio=increase,crop={config['w']}:{config['h']}"
                
                if config['ext'] == 'jpg':
                    args = [
                        '-vf', vf_scale_crop,
                        '-threads', '2', 
                        '-q:v', config['q'],
                        '-pix_fmt', 'yuv420p'
                    ]
                else:
                    args = [
                        '-vf', vf_scale_crop,
                        '-threads', '2', 
                        '-c:v', 'libaom-av1', 
                        '-still-picture', '1',
                        '-crf', config['crf'],
                        '-cpu-used', '6',
                        '-pix_fmt', 'yuv420p'
                    ]
                
                process_and_save_image(input_path, final_path, args)

        elif kind == 'content_image':
            vf_scale_crop = "scale='min(960,iw)':'min(504,ih)':force_original_aspect_ratio=decrease,crop=trunc(iw/2)*2:trunc(ih/2)*2"

            final_path = os.path.join(directory, 'processed.avif')

            args = [
                '-vf', vf_scale_crop,
                '-threads', '2',
                '-c:v', 'libaom-av1',
                '-still-picture', '1',
                '-crf', '16',
                '-cpu-used', '6',
                '-pix_fmt', 'yuv420p'
            ]
            
            process_and_save_image(input_path, final_path, args)

    return f"Successfully processed {kind} for {relative_path}"
