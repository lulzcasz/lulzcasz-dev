from pathlib import Path
from django.db import models
from django.utils.text import slugify


def sponsor_image_upload_to(instance, filename):
    return f"sponsors/{slugify(instance.name)}{Path(filename).suffix.lower()}"


class Sponsor(models.Model):
    name = models.CharField(max_length=40, unique=True)
    url = models.URLField(blank=True, null=True)
    banner = models.ImageField(upload_to=sponsor_image_upload_to, null=True, blank=True)

    def __str__(self):
        return self.name
