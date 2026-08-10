from os.path import splitext
from django.utils.text import slugify


def store_logo_path(instance, filename):
    _, ext = splitext(filename)

    return f'stores/{slugify(instance.name)}{ext}'
