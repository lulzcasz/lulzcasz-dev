from django.contrib import admin
from blog.models import Genre, Category, PostProduct, Post


class PostProductInline(admin.TabularInline):
    model = PostProduct
    extra = 1
    ordering = ['order']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'created_at', 'updated_at')

    inlines = [PostProductInline]

    def get_exclude(self, request, obj=None):
        if not obj:
            return ('content', )

        return super().get_exclude(request, obj)
