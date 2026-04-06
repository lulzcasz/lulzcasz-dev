from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from about.tasks.image import process_image
from about.models import Profile


@receiver(post_save, sender=Profile)
def avatar_profile_save(sender, instance, created, **kwargs):
    if getattr(instance, '_avatar_changed', False) and instance.avatar:
        transaction.on_commit(lambda: process_image.delay(instance.avatar.name))
