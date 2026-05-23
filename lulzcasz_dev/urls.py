from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('blog/', include('blog.urls')),
    path('', include('common.urls')),
    path('', include('portfolio.urls')),
]
