from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('about.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('', include('blog.urls')),
]
