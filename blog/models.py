from common.models import ContentBase, TaxonomyBase
from django.db.models import (
    SET_NULL,
    Count,
    ForeignKey,
    ManyToManyField,
    Q,
    DateTimeField,
    BooleanField,
    PositiveSmallIntegerField,
    Model,
    CASCADE,
)
from django.urls import reverse
from taggit.managers import TaggableManager
from products.models import Product
from django.utils import timezone


class Genre(TaxonomyBase):
    pass


class Category(TaxonomyBase):
    class Meta:
        verbose_name_plural = 'categories'


class PostProduct(Model):
    post = ForeignKey('Post', on_delete=CASCADE)
    product = ForeignKey(Product, on_delete=CASCADE)
    order = PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('post', 'product')

    def __str__(self):
        return f"{self.post.title} - {self.product.name}"


class Post(ContentBase):
    is_featured = BooleanField(default=False)
    published_at = DateTimeField(null=True, editable=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    post_genre = ForeignKey(
        Genre, on_delete=SET_NULL, null=True, blank=True, related_name="posts",
    )
    category = ForeignKey(
        Category, on_delete=SET_NULL, null=True, blank=True, related_name="posts",
    )
    tags = TaggableManager(blank=True)
    products = ManyToManyField(Product, through=PostProduct, blank=True)

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_ordered_products(self):
        return self.products.all().order_by('postproduct__order')

    def get_related_posts(self):
        tag_ids = list(self.tags.values_list("id", flat=True))

        if not tag_ids:
            return Post.objects.none()

        return (
            Post.objects.filter(
                is_published=True,
                tags__in=tag_ids,
            )
            .exclude(pk=self.pk)
            .annotate(shared_tag_count=Count("tags", filter=Q(tags__in=tag_ids)))
            .order_by("-shared_tag_count")
            .only("id", "title", "slug")[:3]
        )

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"post_slug": self.slug})
