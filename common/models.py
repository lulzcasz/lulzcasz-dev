from django.db.models import Model, CharField, SlugField
from django.utils.text import slugify
from django.db.models import (
    Model, CharField, SlugField, ImageField, BooleanField, DateTimeField
)
from tinymce.models import HTMLField
from common.utils import post_image_path
from django.utils import timezone


class TaxonomyBase(Model):
    name = CharField("nome", max_length=32, unique=True)
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
    title = CharField("título", max_length=60, unique=True)
    slug = SlugField(max_length=60, unique=True, blank=True)
    description = CharField("descrição", max_length=145, blank=True)
    cover = ImageField("capa", upload_to=post_image_path, blank=True)
    content = HTMLField("conteúdo", blank=True)
    is_featured = BooleanField("destaque", default=False)
    is_published = BooleanField("publicado", default=False)
    published_at = DateTimeField("publicado em", null=True, editable=False)
    created_at = DateTimeField("criado em", auto_now_add=True)
    updated_at = DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.is_published == True and not self.published_at:
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


class Technology(TaxonomyBase):
    color = CharField("cor", max_length=7)
    
    class Meta(TaxonomyBase.Meta):
        verbose_name = 'tecnologia'
