from common.utils.upload_to import post_image_path
from django.db.models import (
    BooleanField,
    CharField,
    ImageField,
    Model,
    SlugField,
    UUIDField,
)
from django.utils.text import slugify
from tinymce.models import HTMLField
from uuid import uuid4


class ColorMixin(Model):
    color = CharField("cor", max_length=7)

    @property
    def text_color(self):
        hex_color = self.color.lstrip("#")

        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            return "#000000" if luminance > 128 else "#ffffff"

        return "#ffffff"

    class Meta:
        abstract = True


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
    uuid = UUIDField(default=uuid4, editable=False, unique=True)
    title = CharField("título", max_length=60, unique=True)
    slug = SlugField(max_length=60, unique=True, blank=True)
    description = CharField("descrição", max_length=145, blank=True)
    cover = ImageField("capa", upload_to=post_image_path, blank=True)
    content = HTMLField("conteúdo", blank=True)
    is_published = BooleanField("publicado", default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
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

    def __str__(self):
        return self.title


class Technology(ColorMixin, TaxonomyBase):
    class Meta(TaxonomyBase.Meta):
        verbose_name = "tecnologia"
