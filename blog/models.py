from uuid import uuid4

from django.db.models import (
    SET_NULL,
    BooleanField,
    CharField,
    Count,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Q,
    SlugField,
    TextField,
    UUIDField,
)
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import get_language
from parler.models import TranslatableModel, TranslatedFields

from blog.utils.upload_to import article_image_path
from sponsors.models import Sponsor


class BaseTaxonomy(TranslatableModel):
    class Meta:
        abstract = True

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"{self.__class__.__name__} #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Section(BaseTaxonomy):
    translations = TranslatedFields(
        name=CharField(max_length=32),
        slug=SlugField(max_length=32, blank=True),
        meta={
            "unique_together": [
                ("language_code", "name"),
                ("language_code", "slug"),
            ]
        },
    )


class Category(BaseTaxonomy):
    translations = TranslatedFields(
        name=CharField(max_length=32),
        slug=SlugField(max_length=32, blank=True),
        sponsor=ForeignKey(Sponsor, on_delete=SET_NULL, null=True, blank=True),
        meta={
            "unique_together": [
                ("language_code", "name"),
                ("language_code", "slug"),
            ]
        },
    )

    class Meta:
        verbose_name_plural = "categories"


class Tag(BaseTaxonomy):
    translations = TranslatedFields(
        name=CharField(max_length=32),
        slug=SlugField(max_length=32, blank=True),
        meta={
            "unique_together": [
                ("language_code", "name"),
                ("language_code", "slug"),
            ]
        },
    )


class Article(TranslatableModel):
    uuid = UUIDField(default=uuid4, editable=False, unique=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    published_at = DateTimeField(null=True, blank=True)
    is_featured = BooleanField(default=False)

    translations = TranslatedFields(
        title=CharField(max_length=60),
        slug=SlugField(max_length=60, blank=True),
        description=CharField(max_length=160, blank=True),
        content=TextField(blank=True),
        meta={
            "unique_together": [
                ("language_code", "title"),
                ("language_code", "slug"),
            ]
        },
    )

    cover = ImageField(upload_to=article_image_path, blank=True)
    section = ForeignKey(
        Section,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    category = ForeignKey(
        Category,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    tags = ManyToManyField(Tag, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)

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
                published_at__lte=timezone.now(),
                translations__language_code=current_lang,
                tags__in=tag_ids,
            )
            .exclude(pk=self.pk)
            .annotate(shared_tag_count=Count("tags", filter=Q(tags__in=tag_ids)))
            .order_by("-shared_tag_count")[:3]
        )

    def get_published_languages(self):
        if self.published_at and self.published_at <= timezone.now():
            return [translation.language_code for translation in self.translations.all()]
        return []

    def get_absolute_url(self):
        current_lang = get_language()
        slug = self.safe_translation_getter("slug", language_code=current_lang)

        if not slug:
            slug = getattr(self, "slug", None)

        if not slug:
            return "#"

        try:
            return reverse("article-detail", kwargs={"article_slug": slug})
        except NoReverseMatch:
            return "#"

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Article #{self.pk}"
