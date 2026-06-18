from blog.views import (
    index,
    article_detail,
    articles,
    articles_by_category,
    articles_by_kind,
    articles_by_tag,
)
from django.urls import path

urlpatterns = [
    path("", index, name="blog"),
    path("todos-os-articles/", articles, name="all-articles"),
    path("<slug:article_slug>/", article_detail, name="article-detail"),
    path("generos/<str:kind_slug>/", articles_by_kind, name="articles-by-kind"),
    path(
        "categorias/<slug:category_slug>/", articles_by_category, name="articles-by-category"
    ),
    path("tags/<slug:tag_slug>/", articles_by_tag, name="articles-by-tag"),
]
