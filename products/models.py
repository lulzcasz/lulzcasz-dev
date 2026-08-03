from django.db.models import (
    CASCADE, FileField, ForeignKey, ImageField, Model, URLField, CharField, UUIDField
)
from products.utils.upload_to import store_logo_path, product_image_path
from uuid import uuid4
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import get_language


class Store(Model):
    name = CharField(max_length=16, unique=True)
    logo = FileField(upload_to=store_logo_path)
    color = CharField(max_length=7)

    def __str__(self):
        return self.name


class Product(TranslatableModel):
    uuid = UUIDField(default=uuid4, editable=False, unique=True)
    translations = TranslatedFields(
        name = CharField(max_length=128),
        meta={
            'unique_together': [
                ('language_code', 'name'),
            ]
        }
    )
    image = ImageField(null=True, blank=True, upload_to=product_image_path)

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

    def get_active_links(self):
        current_lang = get_language()
        active_links = []
        
        for link in self.links.all():
            url = link.safe_translation_getter('url', language_code=current_lang, any_language=False)

            if url and url.strip():
                link.set_current_language(current_lang)
                active_links.append(link)
                
        return active_links


class AffiliateLink(TranslatableModel):
    translations = TranslatedFields(
        url = URLField(max_length=500, blank=True, null=True),
    )
    product = ForeignKey(Product, on_delete=CASCADE, related_name="links")
    store = ForeignKey(Store, on_delete=CASCADE, related_name="links")
    
    def __str__(self):
        return f"{self.store.name} - {self.product.name}"
