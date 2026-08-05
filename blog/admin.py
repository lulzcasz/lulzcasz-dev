from django.contrib import admin
from blog.models import Kind, Category, Tag, Article
from parler.admin import TranslatableAdmin


@admin.register(Kind)
class KindAdmin(TranslatableAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    pass


@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(TranslatableAdmin):
    readonly_fields = ('uuid', 'created_at', 'updated_at')

    def get_exclude(self, request, obj=None):
        if not obj:
            return ('content', )

        return super().get_exclude(request, obj)
