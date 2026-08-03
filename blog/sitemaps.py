from django.contrib.sitemaps import Sitemap
from blog.models import Article

class ArticleSitemap(Sitemap):
    changefreq = "weekly" 
    priority = 0.8
    i18n = True
    alternates = True

    def items(self):
        return Article.objects.filter(
            translations__is_published=True
        ).order_by('-pk').distinct()

    def lastmod(self, obj):
        return obj.updated_at
