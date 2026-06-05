from django.urls import path
from common.views import tinymce_upload_image, tinymce_upload_video


urlpatterns = [
    path(
        'tinymce/upload-image/', tinymce_upload_image, name='tinymce-upload-image',
    ),
    path(
        'tinymce/upload-video/', tinymce_upload_video, name='tinymce-upload-media',
    ),
    
]
