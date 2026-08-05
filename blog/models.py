from django.db.models import (
    SET_NULL,
    Count,
    ForeignKey,
    Q,
    BooleanField,
    CharField,
    SlugField,
    DateTimeField,
    ImageField,
    UUIDField,
    ManyToManyField,
)
from django.urls import reverse
from tinymce.models import HTMLField
from uuid import uuid4
from django.utils.text import slugify
from django.utils import timezone
from blog.utils.upload_to import article_image_path
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import get_language


class BaseTaxonomy(TranslatableModel):
    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Kind(BaseTaxonomy):
    translations = TranslatedFields(
        name=CharField(max_length=32),
        slug=SlugField(max_length=32, blank=True),
        meta={
            'unique_together': [('language_code', 'name'), ('language_code', 'slug')]
        }
    )


class Category(BaseTaxonomy):
    translations = TranslatedFields(
        name=CharField(max_length=32),
        slug=SlugField(max_length=32, blank=True),
        meta={
            'unique_together': [('language_code', 'name'), ('language_code', 'slug')]
        }
    )

    class Meta:
        verbose_name_plural = 'categories'


class Tag(BaseTaxonomy):
    translations = TranslatedFields(
        name=CharField(max_length=32),
        slug=SlugField(max_length=32, blank=True),
        meta={
            'unique_together': [('language_code', 'name'), ('language_code', 'slug')]
        }
    )


class Article(TranslatableModel):
    uuid = UUIDField(default=uuid4, editable=False, unique=True)
    translations = TranslatedFields(
        title = CharField(max_length=60, unique=True),
        slug = SlugField(max_length=60, unique=True, blank=True),
        description = CharField(max_length=145, blank=True),
        content = HTMLField(blank=True),
        created_at = DateTimeField(auto_now_add=True),
        updated_at = DateTimeField(auto_now=True),
        is_published = BooleanField(default=False),
        published_at = DateTimeField(null=True, editable=False),
        is_featured = BooleanField(default=False)
    )
    cover = ImageField(upload_to=article_image_path, blank=True)
    kind = ForeignKey(
        Kind, on_delete=SET_NULL, null=True, blank=True, related_name="articles",
    )
    category = ForeignKey(
        Category, on_delete=SET_NULL, null=True, blank=True, related_name="articles",
    )
    tags = ManyToManyField(Tag, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        self._cover_changed = False
        if self.cover:
            if self.pk:
                try:
                    old_obj = self.__class__.objects.get(pk=self.pk)
                    if old_obj.cover != self.cover:
                        self._cover_changed = True
                except self.__class__.DoesNotExist:
                    pass
            else:
                self._cover_changed = True

        super().save(*args, **kwargs)

    def get_related_articles(self):
        tag_ids = list(self.tags.values_list("id", flat=True))

        if not tag_ids:
            return Article.objects.none()

        current_lang = self.get_current_language()

        return (
            Article.objects.filter(
                translations__is_published=True,
                translations__language_code=current_lang,
                tags__in=tag_ids,
            )
            .exclude(pk=self.pk)
            .annotate(shared_tag_count=Count("tags", filter=Q(tags__in=tag_ids)))
            .order_by("-shared_tag_count")[:3] 
        )

    def get_absolute_url(self):
        current_lang = get_language()
        
        slug = self.safe_translation_getter('slug', language_code=current_lang)

        if not slug:
            slug = self.slug 

        return reverse("article-detail", kwargs={"article_slug": slug})

    def __str__(self):
        return self.title
