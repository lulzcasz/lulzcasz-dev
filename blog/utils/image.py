import os
import subprocess
import tempfile
import shutil
from contextlib import contextmanager
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


@contextmanager
def download_to_temp(relative_path):
    _, ext = os.path.splitext(relative_path)
    temp_in = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    try:
        with default_storage.open(relative_path, 'rb') as remote_file:
            shutil.copyfileobj(remote_file, temp_in)
        temp_in.close()
        yield temp_in.name
    finally:
        if os.path.exists(temp_in.name):
            os.remove(temp_in.name)


def process_and_save_image(input_path, final_storage_path, ffmpeg_args):
    _, ext = os.path.splitext(final_storage_path)
    
    temp_out = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    temp_out.close()
    
    try:
        cmd = ['ffmpeg', '-y', '-i', input_path] + ffmpeg_args + [temp_out.name]
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        
        with open(temp_out.name, 'rb') as f:
            content = f.read()
            if default_storage.exists(final_storage_path):
                default_storage.delete(final_storage_path)
            default_storage.save(final_storage_path, ContentFile(content))
            
    finally:
        if os.path.exists(temp_out.name):
            os.remove(temp_out.name)
