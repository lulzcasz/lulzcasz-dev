from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from blog.models import Section, Category, Tag, Article


@admin.register(Section)
class SectionAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    search_fields = ('translations__name', 'translations__slug')


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    search_fields = ('translations__name', 'translations__slug')


@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    search_fields = ('translations__name', 'translations__slug')


@admin.register(Article)
class ArticleAdmin(TranslatableAdmin):
    list_display = ('title', 'article_status', 'published_at', 'section', 'category', 'is_featured')
    list_filter = ('section', 'category')
    search_fields = ('translations__title', 'translations__description')
    filter_horizontal = ('tags',)
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'cover_preview')

    def article_status(self, obj):
        if not obj.published_at:
            return format_html('<span style="color: #6b7280; font-weight: bold;">Draft</span>')
        elif obj.published_at > timezone.now():
            return format_html('<span style="color: #f59e0b; font-weight: bold;">Scheduled</span>')
        return format_html('<span style="color: #10b981; font-weight: bold;">Published</span>')
    article_status.short_description = 'Status'

    def cover_preview(self, obj):
        if obj.cover:
            return format_html('<img src="{}" style="max-height: 150px; border-radius: 6px;" />', obj.cover.url)
        return "No cover uploaded yet."
    cover_preview.short_description = 'Cover Preview'

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('General Information', {
                'fields': ('title', 'slug', 'description', 'cover', 'cover_preview')
            }),
            ('Taxonomy', {
                'fields': ('section', 'category', 'tags')
            }),
            ('Publishing Settings', {
                'fields': ('published_at', 'is_featured')
            }),
            ('System Info (Read-Only)', {
                'fields': ('uuid', 'created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        ]

        if obj:
            fieldsets.insert(1, ('Content', {'fields': ('content',)}))

        return fieldsets
