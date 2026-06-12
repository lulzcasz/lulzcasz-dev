from django.db.models import (
    CASCADE, FileField, ForeignKey, ImageField, Model, URLField, CharField, UUIDField
)
from products.utils.upload_to import store_logo_path, product_image_path
from uuid import uuid4


class Store(Model):
    name = CharField(max_length=16, unique=True)
    logo = FileField(upload_to=store_logo_path)
    color = CharField(max_length=7)

    def __str__(self):
        return self.name


class Product(Model):
    uuid = UUIDField(default=uuid4, editable=False, unique=True)
    name = CharField(max_length=32, unique=True)
    description = CharField(max_length=160, blank=True)
    image = ImageField(upload_to=product_image_path)

    def save(self, *args, **kwargs):
        self._image_changed = False

        try:
            old_product = Product.objects.get(pk=self.pk)
            if old_product.image != self.image:
                self._image_changed = True
        except Product.DoesNotExist:
            self._image_changed = True

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AffiliateLink(Model):
    product = ForeignKey(Product, on_delete=CASCADE, related_name="links")
    store = ForeignKey(Store, on_delete=CASCADE, related_name="links")
    url = URLField(max_length=500)

    def __str__(self):
        return f"{self.store.name} - {self.product.name}"
