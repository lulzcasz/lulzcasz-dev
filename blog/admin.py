from django.contrib import admin
from blog.models import Kind, Category, Article


@admin.register(Kind)
class KindAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'created_at', 'updated_at')

    def get_exclude(self, request, obj=None):
        if not obj:
            return ('content', )

        return super().get_exclude(request, obj)
