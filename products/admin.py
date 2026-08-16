from django.contrib import admin
from parler.admin import TranslatableTabularInline
from unfold.admin import ModelAdmin, TabularInline
from .models import Store, Product, AffiliateLink

class AffiliateLinkInline(TranslatableTabularInline, TabularInline):
    model = AffiliateLink
    extra = 0
    fields = ('store', 'url')

@admin.register(Store)
class StoreAdmin(ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name', )
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    readonly_fields = ('id',)
    inlines = [AffiliateLinkInline]

    fieldsets = (
        ('Product Details', {
            'fields': ('name',)
        }),
        ('System Info', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
