from django.db.models import (
    Model,
    CharField,
    TextField,
    ImageField,
    ManyToManyField,
    URLField,
    BooleanField,
    SlugField,
)
from django.utils.text import slugify
from tinymce.models import HTMLField
from django.urls import reverse
from common.utils import post_image_path
from portfolio.utils.upload_to import profile_avatar_path
from common.models import TaxonomyBase, ContentBase, Technology
from taggit.managers import TaggableManager


class Link(Model):
    name = CharField("nome", max_length=16)
    link = URLField(max_length=255)
    color = CharField("cor", max_length=7)

    def __str__(self):
        return self.name


class Profile(Model):
    name = CharField("nome", max_length=40)
    subtitle = CharField("subtítulo", max_length=128)
    avatar = ImageField(upload_to=profile_avatar_path)
    bio = TextField(max_length=800)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfil'

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
    

class Project(ContentBase):
    repository = URLField("repositório", blank=True, null=True)
    live = URLField("ao vivo", blank=True, null=True)
    tags = TaggableManager(blank=True)
    technologies = ManyToManyField(
        Technology, blank=True, related_name='projects', verbose_name="tecnologias"
    )

    class Meta:
        verbose_name = 'projeto'

    def get_absolute_url(self):
        return reverse("project-detail", kwargs={"project_slug": self.slug})
