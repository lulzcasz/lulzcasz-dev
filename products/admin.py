from django.contrib import admin
from products.models import Store, Product, AffiliateLink


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    pass
