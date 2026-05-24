from blog.views import (
    index,
    post_detail,
    posts,
    posts_by_category,
    posts_by_genre,
    posts_by_tag,
)
from django.urls import path

urlpatterns = [
    path("", index, name="blog"),
    path("todos-os-posts/", posts, name="all-posts"),
    path("<slug:post_slug>/", post_detail, name="post-detail"),
    path("generos/<str:genre_slug>/", posts_by_genre, name="posts-by-genre"),
    path(
        "categorias/<slug:category_slug>/", posts_by_category, name="posts-by-category"
    ),
    path("tags/<slug:tag_slug>/", posts_by_tag, name="posts-by-tag"),
]
