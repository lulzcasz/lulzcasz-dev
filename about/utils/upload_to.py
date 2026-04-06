from os.path import splitext
from uuid import uuid4
from django.utils.timezone import now


def profile_avatar_path(instance, filename):
    return f'images/avatars/{now().strftime("%Y/%m/%d")}/{uuid4()}/raw{splitext(filename)[1]}'
