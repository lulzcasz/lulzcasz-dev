from uuid import uuid4

def article_image_path(instance, filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else 'img'
    
    return f'articles/{instance.uuid}/cover/{uuid4()}/original.{ext}'
