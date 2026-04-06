from django.db.models import (
    Model,
    CharField,
    TextField,
    ImageField,
    OneToOneField,
    CASCADE,
    PositiveSmallIntegerField,
)
from blog.models import Article
from about.utils.upload_to import profile_avatar_path


class Link(Model):
    name = CharField("nome", max_length=16)
    link = CharField(max_length=255)
    color = CharField("cor", max_length=7)
    bg_color = CharField("cor do fundo", max_length=7)

    def __str__(self):
        return self.name


class Profile(Model):
    name = CharField("nome", max_length=40)
    subtitle = CharField("subtítulo", max_length=128)
    avatar = ImageField(upload_to=profile_avatar_path)
    bio = TextField(max_length=800)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

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


class HighlightArticle(Model):
    article = OneToOneField(Article, CASCADE, verbose_name='artigo')
    order = PositiveSmallIntegerField('ordem', default=0)

    class Meta:
        verbose_name = 'artigo em destaque'
        verbose_name_plural = 'artigos em destaque'
        ordering = ['order', '-article__published_at']

    def __str__(self):
        return self.article.title 
