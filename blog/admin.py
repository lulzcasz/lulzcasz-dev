from django.contrib import admin
from blog.models import Genre, Category, Post
from products.models import Product


class ProductInline(admin.TabularInline):
    model = Post.products.through
    extra = 1

    fields = ('product_id_display', 'product')

    readonly_fields = ('product_id_display',)

    @admin.display(description="product id")
    def product_id_display(self, instance):
        if instance.pk and instance.product:
            return f"ID: {instance.product.id}"
        return "-"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'created_at', 'updated_at')

    inlines = [ProductInline]

    exclude = ('products',)

    def get_exclude(self, request, obj=None):
        if not obj:
            return ('content', )

        return super().get_exclude(request, obj)
