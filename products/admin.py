from django.contrib import admin
from products.models import Store, Product, AffiliateLink
from parler.admin import TranslatableAdmin


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    pass


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(TranslatableAdmin):
    pass
