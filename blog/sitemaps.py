# sitemaps.py
from django.contrib.sitemaps import Sitemap
from blog.models import Article

class ArticleSitemap(Sitemap):
    changefreq = "weekly" 
    priority = 0.8

    def items(self):
        return Article.objects.filter(is_published=True).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at
