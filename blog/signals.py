from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from blog.tasks.image import process_image
from blog.models import Article


@receiver(post_save)
def cover_post_save(sender, instance, created, **kwargs):
    if not isinstance(instance, Article):
        return
    
    if getattr(instance, '_cover_changed', False):
        transaction.on_commit(lambda: process_image.delay(instance.cover.name, 'cover'))
