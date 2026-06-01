from os.path import splitext
from uuid import uuid4


def post_image_path(instance, filename):
    return f'publications/{instance.uuid}/cover/{uuid4()}/raw{splitext(filename)[1]}'
