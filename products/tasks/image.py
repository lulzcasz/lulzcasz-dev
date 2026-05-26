import os
import subprocess
import tempfile
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@shared_task(bind=True)
def process_image(self, relative_path):
    directory = os.path.dirname(relative_path)

    # Captura a extensão original para não quebrar a leitura do ffmpeg
    _, ext = os.path.splitext(relative_path)

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_in:
        with default_storage.open(relative_path, 'rb') as storage_file:
            temp_in.write(storage_file.read())
        temp_input_path = temp_in.name

    temp_file_out = tempfile.NamedTemporaryFile(suffix='.avif', delete=False)
    temp_file_out.close()
    temp_output_path = temp_file_out.name

    try:
        # Salva ao lado da imagem original dentro da pasta do UUID
        final_storage_path = os.path.join(directory, 'processed.avif')

        # Reduz para 128x128 preservando a proporção (sem cortar as bordas do produto)
        product_vf = "scale=128:128:force_original_aspect_ratio=decrease"

        cmd = [
            'ffmpeg', '-y',
            '-i', temp_input_path,
            '-vf', product_vf,
            '-c:v', 'libaom-av1',
            '-still-picture', '1',
            '-crf', '15',  # Reduzido para manter alta qualidade
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

    return f"Successfully processed product image for {relative_path}"
