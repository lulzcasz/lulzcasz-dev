from uuid import uuid4


def article_image_path(instance, filename):
    return f'articles/{instance.uuid}/cover/{uuid4()}/raw.webp'
