from blog.views import (
    index,
    article_detail,
    articles,
    articles_by_category,
    articles_by_section,
    articles_by_tag,
)
from django.urls import path
from blog.views import tinymce_upload_image, tinymce_upload_video


urlpatterns = [
    path("", index, name="blog"),
    path("todos-os-articles/", articles, name="all-articles"),
        path(
        'tinymce/upload-image/', tinymce_upload_image, name='tinymce-upload-image',
    ),
    path(
        'tinymce/upload-video/', tinymce_upload_video, name='tinymce-upload-media',
    ),
    path("<slug:article_slug>/", article_detail, name="article-detail"),
    path("generos/<str:section_slug>/", articles_by_section, name="articles-by-section"),
    path(
        "categorias/<slug:category_slug>/", articles_by_category, name="articles-by-category"
    ),
    path("tags/<slug:tag_slug>/", articles_by_tag, name="articles-by-tag"),
]
