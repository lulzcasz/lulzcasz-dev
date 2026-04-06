import os
import subprocess
import tempfile
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@shared_task(bind=True)
def process_image(self, relative_path):
    try:
        input_source = default_storage.path(relative_path)
    except NotImplementedError:
        input_source = default_storage.url(relative_path)

    directory = os.path.dirname(relative_path)

    temp_file = tempfile.NamedTemporaryFile(suffix='.avif', delete=False)
    temp_file.close()
    temp_output_path = temp_file.name

    try:
        final_storage_path = os.path.join(directory, 'avatar.avif')

        avatar_vf = "crop='min(iw,ih)':'min(iw,ih)',scale=256:256"

        cmd = [
            'ffmpeg', '-y',
            '-i', input_source,
            '-vf', avatar_vf,
            '-pix_fmt', 'yuv420p',
            '-c:v', 'libaom-av1',
            '-still-picture', '1',
            '-crf', '25',
            '-cpu-used', '4',
            temp_output_path
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open(temp_output_path, 'rb') as f:
            content = f.read()
            if default_storage.exists(final_storage_path):
                default_storage.delete(final_storage_path)
            default_storage.save(final_storage_path, ContentFile(content))

    except subprocess.CalledProcessError as e:
        raise e
    
    finally:
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)

    return f"Successfully processed avatar for {relative_path}"
