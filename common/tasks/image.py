import os
import subprocess
import tempfile
import shutil
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image

@shared_task(bind=True)
def process_image(self, relative_path, kind):
    directory = os.path.dirname(relative_path)

    temp_in = tempfile.NamedTemporaryFile(suffix='.raw', delete=False)
    temp_out = tempfile.NamedTemporaryFile(suffix='.avif', delete=False)
    temp_in.close()
    temp_out.close()

    try:
        with default_storage.open(relative_path, 'rb') as remote_file:
            with open(temp_in.name, 'wb') as local_file:
                shutil.copyfileobj(remote_file, local_file)

        if kind == 'cover':
            versions = {
                'small': (400, 210, 6),
                'medium': (600, 315, 10),
                'large': (1200, 630, 16),
            }

            for suffix, (width, height, crf) in versions.items():
                final_storage_path = os.path.join(directory, f"{suffix}.avif")

                cmd = [
                    'ffmpeg', '-y',
                    '-i', temp_in.name,
                    '-vf', f"scale='if(lt(iw/ih,{width}/{height}),{width},-2)':'if(lt(iw/ih,{width}/{height}),-2,{height})',crop={width}:{height}",
                    '-pix_fmt', 'yuv420p',
                    '-c:v', 'libaom-av1',
                    '-still-picture', '1',
                    '-crf', str(crf),
                    temp_out.name
                ]
                
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                with open(temp_out.name, 'rb') as f:
                    content = f.read()
                    default_storage.save(final_storage_path, ContentFile(content))

        elif kind == 'content_image':
            final_storage_path = os.path.join(directory, 'processed.avif')
            is_animated = False

            try:
                with Image.open(temp_in.name) as img:
                    is_animated = getattr(img, 'is_animated', False)
            except Exception as e:
                raise e

            if is_animated:
                cmd = [
                    'ffmpeg', '-y',
                    '-i', temp_in.name,
                    '-c:v', 'libsvtav1',
                    '-crf', '38',
                    '-preset', '8',
                    '-vf', "scale='min(1024,iw)':-2:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    '-pix_fmt', 'yuv420p',
                    temp_out.name
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-i', temp_in.name,
                    '-vf', "scale='min(1024,iw)':'min(576,ih)':force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    '-pix_fmt', 'yuv420p',
                    '-c:v', 'libaom-av1',
                    '-still-picture', '1',
                    '-crf', '25',
                    '-cpu-used', '4',
                    temp_out.name
                ]

            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            with open(temp_out.name, 'rb') as f:
                content = f.read()
                default_storage.save(final_storage_path, ContentFile(content))

    except subprocess.CalledProcessError as e:
        raise e
    
    finally:
        if os.path.exists(temp_in.name):
            os.remove(temp_in.name)
        if os.path.exists(temp_out.name):
            os.remove(temp_out.name)

    return f"Successfully processed {kind} for {relative_path}"
