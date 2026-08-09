from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from products.models import Store, Product, AffiliateLink


class AffiliateLinkInline(TranslatableTabularInline):
    model = AffiliateLink
    extra = 1
    fields = ('store', 'url')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_badge')
    search_fields = ('name',)

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 16px; height: 16px; background-color: {}; '
                'border-radius: 50%; border: 1px solid #ccc;"></div>', 
                obj.color
            )
        return "-"
    color_badge.short_description = 'Color'


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('name', 'image_preview')
    search_fields = ('translations__name',)
    readonly_fields = ('uuid', 'image_preview')
    inlines = [AffiliateLinkInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'

    fieldsets = (
        ('Product Details', {
            'fields': ('name', 'image', 'image_preview')
        }),
        ('System Info', {
            'fields': ('uuid',),
            'classes': ('collapse',)
        }),
    )
