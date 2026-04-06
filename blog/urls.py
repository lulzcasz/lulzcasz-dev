from django.urls import path
from blog.views import (
    tinymce_upload_image,
    index,
    articles,
    article_detail,
    articles_by_format,
    articles_by_category,
    articles_by_tag,
)

urlpatterns = [
    path('', index, name="home"),
    path('todos-os-artigos/', articles, name="all-articles"),
    path(
        'tinymce/upload-image/', tinymce_upload_image, name='tinymce-upload-image',
    ),
    path('<slug:article_slug>/', article_detail, name='article-detail'),
    path('formatos/<str:format_slug>/', articles_by_format, name='articles-by-format'),
    path(
        'categorias/<slug:category_slug>/', articles_by_category, name='articles-by-category'
    ),
    path('tags/<slug:tag_slug>/', articles_by_tag, name='articles-by-tag'),
]
