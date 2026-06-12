from common.models import ContentBase, TaxonomyBase
from django.db.models import (
    CharField, ImageField, ManyToManyField, Model, TextField, URLField,
)
from django.urls import reverse
from portfolio.utils.upload_to import profile_avatar_path
from taggit.managers import TaggableManager


class ColorMixin(Model):
    color = CharField(max_length=7)

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


class Link(ColorMixin, Model):
    name = CharField(max_length=16)
    link = URLField(max_length=255)

    def __str__(self):
        return self.name


class Profile(Model):
    name = CharField(max_length=40)
    subtitle = CharField(max_length=128)
    avatar = ImageField(upload_to=profile_avatar_path)
    bio = TextField(max_length=800)

    def save(self, *args, **kwargs):
        self.pk = 1
        self._avatar_changed = False

        try:
            old_profile = Profile.objects.get(pk=self.pk)
            if old_profile.avatar != self.avatar:
                self._avatar_changed = True
        except Profile.DoesNotExist:
            self._avatar_changed = True

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Technology(ColorMixin, TaxonomyBase):
    class Meta:
        verbose_name_plural = 'technologies'


class Project(ContentBase):
    repository = URLField(blank=True, null=True)
    live = URLField(blank=True, null=True)
    technologies = ManyToManyField(Technology, blank=True, related_name="projects")

    def get_absolute_url(self):
        return reverse("project-detail", kwargs={"project_slug": self.slug})
