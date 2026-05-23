from django.db.models import (
    Count,
    Q,
    ManyToManyField,
    ForeignKey,
    SET_NULL,
)
from django.urls import reverse
from taggit.managers import TaggableManager
from common.models import TaxonomyBase, ContentBase


class Format(TaxonomyBase):
    class Meta:
        verbose_name = 'formato'


class Category(TaxonomyBase):
    class Meta:
        verbose_name = 'categoria'


class Post(ContentBase):
    post_format = ForeignKey(
        Format,
        SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='formato',
    )
    category = ForeignKey(
        Category, SET_NULL,
        null=True,
        blank=True,
        verbose_name='categoria',
        related_name='posts',
    )
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name = 'post'
        
    def get_related_posts(self):
        tag_ids = list(self.tags.values_list("id", flat=True))

        if not tag_ids:
            return Post.objects.none()

        return (
            Post.objects.filter(
                is_published=True, tags__in=tag_ids,
            )
            .exclude(pk=self.pk)
            .annotate(shared_tag_count=Count("tags", filter=Q(tags__in=tag_ids)))
            .order_by("-shared_tag_count")
            .only("id", "title", "slug")[:3]
        )

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"post_slug": self.slug})
