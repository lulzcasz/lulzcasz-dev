import os
import uuid
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from common.tasks.image import process_image
from common.tasks.video import process_video


@login_required
def tinymce_upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']
        raw_post_uuid = request.POST.get('post_uuid')

        try:
            valid_uuid = str(uuid.UUID(raw_post_uuid))
            folder_path = f"publications/{valid_uuid}/content"
        except (ValueError, TypeError):
            date_path = timezone.now().strftime('%Y/%m/%d')
            folder_path = f"images/content/unassigned/{date_path}"

        image_token = str(uuid.uuid4())
        _, ext = os.path.splitext(upload.name)
        
        relative_path = f"{folder_path}/{image_token}/raw{ext}"

        saved_path = default_storage.save(relative_path, upload)
        file_url = default_storage.url(saved_path)

        process_image.delay(saved_path, 'content_image')
        
        return JsonResponse({'location': file_url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def tinymce_upload_video(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']
        raw_post_uuid = request.POST.get('post_uuid')

        try:
            valid_uuid = str(uuid.UUID(raw_post_uuid))
            folder_path = f"publications/{valid_uuid}/content"
        except (ValueError, TypeError):
            date_path = timezone.now().strftime('%Y/%m/%d')
            folder_path = f"videos/content/unassigned/{date_path}"

        video_token = str(uuid.uuid4())
        _, ext = os.path.splitext(upload.name)

        relative_path = f"{folder_path}/{video_token}/raw{ext}"

        saved_path = default_storage.save(relative_path, upload)
        file_url = default_storage.url(saved_path)
        
        process_video.delay(saved_path, 'content_video')
        
        return JsonResponse({'location': file_url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
