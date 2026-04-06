import os
from django import template
from django.core.files.storage import default_storage

register = template.Library()

@register.filter
def variant(image_field, size):
    return default_storage.url(f"{os.path.dirname(image_field.name)}/{size}.avif")
