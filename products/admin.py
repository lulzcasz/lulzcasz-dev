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
    list_display = ('name', )
    search_fields = ('name', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('uuid',)
    inlines = [AffiliateLinkInline]

    fieldsets = (
        ('Product Details', {
            'fields': ('name',)
        }),
        ('System Info', {
            'fields': ('uuid',),
            'classes': ('collapse',)
        }),
    )
