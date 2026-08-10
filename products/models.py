from uuid import uuid4
from django.db.models import (
    CASCADE, ForeignKey, Model, URLField, CharField, UUIDField
)
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import get_language


class Store(Model):
    name = CharField(max_length=16, unique=True)

    def __str__(self):
        return self.name


class Product(Model):
    uuid = UUIDField(default=uuid4, editable=False, unique=True)
    name = CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    def get_active_links(self):
        lang = get_language() 
        active_links = []
        
        for link in self.links.all():
            translation = link.translations.filter(language_code=lang).first()
            
            if translation and translation.url:
                url_str = str(translation.url).strip()
                if url_str:
                    link.resolved_url = url_str
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
