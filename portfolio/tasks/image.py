import os
import subprocess
import tempfile
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@shared_task(bind=True)
def process_image(self, relative_path):
    directory = os.path.dirname(relative_path)

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_in:
        with default_storage.open(relative_path, 'rb') as storage_file:
            temp_in.write(storage_file.read())
        temp_input_path = temp_in.name

    temp_file_out = tempfile.NamedTemporaryFile(suffix='.avif', delete=False)
    temp_file_out.close()
    temp_output_path = temp_file_out.name

    try:
        final_storage_path = os.path.join(directory, 'avatar.avif')

        avatar_vf = "crop='min(iw,ih)':'min(iw,ih)',scale=256:256"

        cmd = [
            'ffmpeg', '-y',
            '-i', temp_input_path,
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
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)

    return f"Successfully processed avatar for {relative_path}"
