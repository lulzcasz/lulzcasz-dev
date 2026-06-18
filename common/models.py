from common.utils.upload_to import article_image_path
from django.db.models import (
    BooleanField, CharField, ImageField, Model, SlugField, UUIDField, DateTimeField
)
from django.utils.text import slugify
from tinymce.models import HTMLField
from uuid import uuid4
from django.utils import timezone


class TaxonomyBase(Model):
    name = CharField(max_length=32, unique=True)
    slug = SlugField(max_length=32, unique=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


class ContentBase(Model):
    uuid = UUIDField(default=uuid4, editable=False, unique=True)
    title = CharField(max_length=60, unique=True)
    slug = SlugField(max_length=60, unique=True, blank=True)
    description = CharField(max_length=145, blank=True)
    cover = ImageField(upload_to=article_image_path, blank=True)
    content = HTMLField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_published = BooleanField(default=False)
    published_at = DateTimeField(null=True, editable=False)

    class Meta:
        abstract = True

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

    def __str__(self):
        return self.title
