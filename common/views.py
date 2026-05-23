import os
from uuid import uuid4
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from common.tasks.image import process_image


@login_required
def tinymce_upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']

        date_path = timezone.now().strftime('%Y/%m/%d')
        token = str(uuid4())
        _, ext = os.path.splitext(upload.name)

        relative_path = f"images/content/{date_path}/{token}/raw{ext}"

        saved_path = default_storage.save(relative_path, upload)
        file_url = default_storage.url(saved_path)

        process_image.delay(saved_path, 'content_image')
        
        return JsonResponse({'location': file_url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)