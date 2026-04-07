from django.contrib import admin
from blog.models import Format, Category, Tag, Article
from django.utils.html import format_html


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'plural_name', 'slug')
    fields = ('name', 'plural_name', 'slug')


@admin.register(Category, Tag)
class CategoryTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'is_featured', 'published_at')
    list_editable = ('status', 'is_featured')
    list_filter = ('status', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'content')

    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('published_at', 'updated_at')

    fieldsets = (
        ("Principal", {
            'fields': ('title', 'slug', 'description', 'content')
        }),
        ("Mídia & Organização", {
            'fields': ('cover', 'article_format', 'category', 'tags')
        }),
        ("Status & Datas", {
            'fields': ('status', 'is_featured', 'published_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
