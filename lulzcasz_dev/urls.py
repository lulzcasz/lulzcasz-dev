from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import TemplateView

from blog.sitemaps import ArticleSitemap

sitemaps = {
    "articles": ArticleSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += i18n_patterns(
    path('', include('blog.urls')),
    prefix_default_language=False 
)
