from django.db.models import (
    CharField,
    DateTimeField,
    ImageField,
    SlugField,
    TextChoices,
    Count,
    Q,
    BooleanField,
    ManyToManyField,
    Model,
    ForeignKey,
    SET_NULL,
)
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from blog.utils import article_image_path
from tinymce.models import HTMLField
from bs4 import BeautifulSoup
import os
from django.core.files.storage import default_storage
from urllib.parse import urlparse


class TaxonomyBase(Model):
    name = CharField("nome", max_length=32, unique=True)
    slug = SlugField(max_length=32, unique=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def slug_source(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.slug_source)
        super().save(*args, **kwargs)


class Format(TaxonomyBase):
    plural_name = CharField("nome plural", max_length=32, unique=True)

    class Meta:
        verbose_name = 'formato'

    @property
    def slug_source(self):
        return self.plural_name


class Category(TaxonomyBase):
    class Meta:
        verbose_name = 'categoria'


class Tag(TaxonomyBase):
    pass


class Article(Model):
    class Status(TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicado"

    article_format = ForeignKey(
        Format,
        SET_NULL,
        null=True,
        blank=True,
        max_length=11,
        related_name='articles',
        verbose_name='formato',
    )
    title = CharField("título", max_length=60, unique=True)
    slug = SlugField(max_length=60, unique=True, blank=True)
    description = CharField("descrição", max_length=145, blank=True)
    cover = ImageField("capa", upload_to=article_image_path, blank=True)
    content = HTMLField("conteúdo", blank=True)
    created_at = DateTimeField("criado em", auto_now_add=True)
    updated_at = DateTimeField("atualizado em", auto_now=True)
    published_at = DateTimeField("publicado em", null=True, editable=False)
    status = CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    category = ForeignKey(
        Category,
        SET_NULL,
        null=True,
        blank=True,
        verbose_name='categoria',
        related_name='articles',
    )
    tags = ManyToManyField(Tag, blank=True, related_name='articles')
    is_featured = BooleanField(default=False, verbose_name="é destaque")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        self._cover_changed = False

        if self.cover:
            if self.pk:
                if Article.objects.get(pk=self.pk).cover != self.cover:
                    self._cover_changed = True
            else:
                self._cover_changed = True
            
        if self.content:
            soup = BeautifulSoup(self.content, 'html.parser')
            images = soup.find_all('img')
            
            modified = False
            for img in images:
                src = img.get('src')
                if not src: 
                    continue

                if 'raw.' in src:
                    try:
                        parsed = urlparse(src)
                        path = parsed.path
                        
                        if 'images/' in path:
                            start_index = path.find('images/')
                            relative_raw_path = path[start_index:] 
                            
                            directory = os.path.dirname(relative_raw_path)
                            relative_avif_path = os.path.join(directory, 'processed.avif')

                            if default_storage.exists(relative_avif_path):
                                path_part, _ = src.rsplit('/', 1)
                                new_src = f"{path_part}/processed.avif"

                                img['data-original'] = src
                                
                                existing_classes = img.get('class', [])
                                if 'zoomable' not in existing_classes:
                                    img['class'] = existing_classes + ['zoomable']

                                img['src'] = new_src
                                
                                modified = True

                    except Exception as e:
                        continue
            
            if modified:
                self.content = str(soup)

        super().save(*args, **kwargs)
        
    def get_related_articles(self):
        tag_ids = list(self.tags.values_list("id", flat=True))

        if not tag_ids:
            return Article.objects.none()

        return (
            Article.objects.filter(
                status=self.Status.PUBLISHED,
                tags__in=tag_ids,
            )
            .exclude(pk=self.pk)
            .annotate(shared_tag_count=Count("tags", filter=Q(tags__in=tag_ids)))
            .order_by("-shared_tag_count")
            .only("id", "title", "slug")[:3]
        )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'artigo'

    def get_absolute_url(self):
        return reverse("article-detail", kwargs={"article_slug": self.slug})
