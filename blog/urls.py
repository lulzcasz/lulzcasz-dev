from django.urls import path
from blog.views import (
    index,
    posts,
    post_detail,
    posts_by_format,
    posts_by_category,
)

urlpatterns = [
    path('', index, name="blog"),
    path('todos-os-posts/', posts, name="all-posts"),
    path('<slug:post_slug>/', post_detail, name='post-detail'),
    path('formatos/<str:format_slug>/', posts_by_format, name='posts-by-format'),
    path(
        'categorias/<slug:category_slug>/', posts_by_category, name='posts-by-category'
    ),
    #path('tags/<slug:tag_slug>/', posts_by_tag, name='posts-by-tag'),
]
