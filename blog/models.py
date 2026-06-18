from common.models import ContentBase, TaxonomyBase
from django.db.models import SET_NULL, Count, ForeignKey, Q, BooleanField
from django.urls import reverse
from taggit.managers import TaggableManager


class Kind(TaxonomyBase):
    pass


class Category(TaxonomyBase):
    class Meta:
        verbose_name_plural = 'categories'


class Article(ContentBase):
    is_featured = BooleanField(default=False)
    kind = ForeignKey(
        Kind, on_delete=SET_NULL, null=True, blank=True, related_name="articles",
    )
    category = ForeignKey(
        Category, on_delete=SET_NULL, null=True, blank=True, related_name="articles",
    )
    tags = TaggableManager(blank=True)

    def get_related_articles(self):
        tag_ids = list(self.tags.values_list("id", flat=True))

        if not tag_ids:
            return Article.objects.none()

        return (
            Article.objects.filter(
                is_published=True,
                tags__in=tag_ids,
            )
            .exclude(pk=self.pk)
            .annotate(shared_tag_count=Count("tags", filter=Q(tags__in=tag_ids)))
            .order_by("-shared_tag_count")
            .only("id", "title", "slug")[:3]
        )

    def get_absolute_url(self):
        return reverse("article-detail", kwargs={"article_slug": self.slug})
