from django.contrib.sitemaps import Sitemap
from blog.models import Article
from django.utils import timezone

class ArticleSitemap(Sitemap):
    changefreq = "weekly" 
    priority = 0.8
    i18n = True
    alternates = True

    def items(self):
        return Article.objects.filter(
            published_at__lte=timezone.now()
        ).prefetch_related('translations').order_by('-pk').distinct()

    def lastmod(self, obj):
        return obj.updated_at
        
    def get_languages_for_item(self, item):
        return item.get_published_languages()
