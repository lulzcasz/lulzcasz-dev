from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',
    "django_htmx",
    'blog',
    'about',
]

TINYMCE_DEFAULT_CONFIG = {
    "height": "800px",
    "width": "100%",
    "menubar": False,
    "plugins": "image codesample directionality fullscreen link lists advlist media preview table code",
    "toolbar": "undo redo | blocks fontsize | bold italic underline strikethrough | align numlist bullist | link image | table media | lineheight outdent indent| forecolor backcolor removeformat | charmap emoticons | code fullscreen preview | pagebreak anchor codesample ltr rtl",
    "toolbar_mode": "wrap",
    'content_css': ['dark', '/static/blog/css/tinymce-content.css'],
    'skin': 'oxide-dark',
    'license_key': 'gpl',
    "images_upload_handler": "upload_image",
    'image_dimensions': False,
    "codesample_languages": [
        {"text": "Arduino", "value": "arduino"},
        {"text": "ARM Assembly", "value": "armasm"},
        {"text": "Atmel AVR Assembly", "value": "asmatmel"},
        {"text": "Bash", "value": "bash"},
        {"text": "C", "value": "c"},
        {"text": "CMake", "value": "cmake"},
        {"text": "C++", "value": "cpp"},
        {"text": "CSS", "value": "css"},
        {"text": "Django/Jinja2", "value": "django"},
        {"text": "Docker", "value": "docker"},
        {"text": "JavaScript", "value": "javascript"},
        {"text": "JSON", "value": "json"},
        {"text": "Makefile", "value": "makefile"},
        {"text": "MongoDB", "value": "mongodb"},
        {"text": "NASM", "value": "nasm"},
        {"text": "PowerShell", "value": "powershell"},
        {"text": "Python", "value": "python"},
        {"text": "SQL", "value": "sql"},
        {"text": "TOML", "value": "toml"},
        {"text": "YAML", "value": "yaml"},
        {"text": "Treeview", "value": "treeview"},
    ],
}

TINYMCE_EXTRA_MEDIA = {
    'js': [
        'blog/js/tinymce-upload-image.js'
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
]

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Santarem'

ROOT_URLCONF = 'lulzcasz_dev.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.explore_items',
            ],
        },
    },
]

WSGI_APPLICATION = 'lulzcasz_dev.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DATABASE_NAME"),
        'USER': os.getenv("DATABASE_USER"),
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv("DATABASE_PORT"),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

STATIC_URL = os.getenv("STATIC_URL")
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
}

AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_ADDRESSING_STYLE = os.getenv('AWS_S3_ADDRESSING_STYLE')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
