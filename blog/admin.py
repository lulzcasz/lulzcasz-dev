from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from tinymce.widgets import TinyMCE
from django.db import models

from blog.models import Section, Category, Tag, Article

@admin.register(Section)
class SectionAdmin(ModelAdmin, TranslatableAdmin):
    list_display = ('name', 'slug')
    search_fields = ('translations__name', 'translations__slug')

@admin.register(Category)
class CategoryAdmin(ModelAdmin, TranslatableAdmin):
    list_display = ('name', 'slug')
    search_fields = ('translations__name', 'translations__slug')

@admin.register(Tag)
class TagAdmin(ModelAdmin, TranslatableAdmin):
    list_display = ('name', 'slug')
    search_fields = ('translations__name', 'translations__slug')

@admin.register(Article)
class ArticleAdmin(ModelAdmin, TranslatableAdmin):
    list_display = ('id', 'title', 'article_status', 'published_at', 'section', 'category', 'is_featured')
    list_display_links = ('id', 'title')
    list_filter = ('section', 'category')
    search_fields = ('translations__title', 'translations__description')
    filter_horizontal = ('tags',)
    
    readonly_fields = (
        'id', 'get_uuid', 'created_at', 'updated_at', 'cover_preview',
        'get_title_en', 'get_title_pt', 
        'get_slug_en', 'get_slug_pt',
        'get_description_en', 'get_description_pt'
    )

    formfield_overrides = {
        models.TextField: {
            "widget": TinyMCE,
        }
    }

    fieldsets = (
        ("Overview", {
            "fields": (
                ("get_title_en", "get_title_pt"),
                ("get_slug_en", "get_slug_pt"),
                ("get_description_en", "get_description_pt"),
            ),
        }),
        ("Content", {
            "fields": ('title', 'slug', 'description', 'content'),
        }),
        ("Settings", {
            "fields": (
                ('published_at', 'is_featured'),
                ('section', 'category'),
                'tags'
            ),
        }),
        ("Media", {
            "fields": ('cover', 'cover_preview'),
        }),
        ("System", {
            "fields": ('id', 'get_uuid', 'created_at', 'updated_at'),
            "classes": ("collapse",)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj is None or not obj.pk:
            if 'content' not in readonly:
                readonly.append('content')
        return readonly

    @display(description="Status", label={
        "Draft": "info",
        "Scheduled": "warning",
        "Published": "success",
    })
    def article_status(self, obj):
        if not obj.published_at:
            return "Draft"
        elif obj.published_at > timezone.now():
            return "Scheduled"
        return "Published"

    @display(description="Cover preview")
    def cover_preview(self, obj):
        if obj.cover:
            return format_html('<img src="{}" class="max-h-48 rounded-lg shadow" />', obj.cover.url)
        return "No cover uploaded yet."

    @display(description="UUID")
    def get_uuid(self, obj):
        if obj and obj.pk:
            return obj.uuid
        return "-"

    @display(description="Title (EN)")
    def get_title_en(self, obj):
        if obj.has_translation('en'):
            return obj.safe_translation_getter('title', language_code='en') or "-"
        return "-"

    @display(description="Title (PT-BR)")
    def get_title_pt(self, obj):
        if obj.has_translation('pt-br'):
            return obj.safe_translation_getter('title', language_code='pt-br') or "-"
        return "-"

    @display(description="Slug (EN)")
    def get_slug_en(self, obj):
        if obj.has_translation('en'):
            return obj.safe_translation_getter('slug', language_code='en') or "-"
        return "-"

    @display(description="Slug (PT-BR)")
    def get_slug_pt(self, obj):
        if obj.has_translation('pt-br'):
            return obj.safe_translation_getter('slug', language_code='pt-br') or "-"
        return "-"

    @display(description="Description (EN)")
    def get_description_en(self, obj):
        if obj.has_translation('en'):
            return obj.safe_translation_getter('description', language_code='en') or "-"
        return "-"

    @display(description="Description (PT-BR)")
    def get_description_pt(self, obj):
        if obj.has_translation('pt-br'):
            return obj.safe_translation_getter('description', language_code='pt-br') or "-"
        return "-"

    def view_on_site(self, obj):
        from django.utils import translation
        from django.urls import reverse

        lang = obj.get_current_language()

        slug = obj.safe_translation_getter('slug', language_code=lang) or obj.slug

        if not slug:
            return None
            
        try:
            with translation.override(lang):
                return reverse("article-detail", kwargs={"article_slug": slug})
        except reverse.NoReverseMatch:
            return None
