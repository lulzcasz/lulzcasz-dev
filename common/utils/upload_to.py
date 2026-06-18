from os.path import splitext
from uuid import uuid4


def article_image_path(instance, filename):
    return f'posts/{instance.uuid}/cover/{uuid4()}/raw{splitext(filename)[1]}'
