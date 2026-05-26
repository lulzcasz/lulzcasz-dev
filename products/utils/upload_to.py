from os.path import splitext
from uuid import uuid4
from django.utils.timezone import now
from django.utils.text import slugify


def store_logo_path(instance, filename):
    _, ext = splitext(filename)

    return f'images/stores/{slugify(instance.name)}{ext}'


def product_image_path(instance, filename):
    return f'images/products/{now().strftime("%Y/%m/%d")}/{uuid4()}/raw{splitext(filename)[1]}'
