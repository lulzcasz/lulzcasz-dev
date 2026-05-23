from django.contrib import admin
from blog.models import Format, Category, Post


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
