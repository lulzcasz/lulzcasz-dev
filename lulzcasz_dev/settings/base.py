from pathlib import Path
import os
import socket

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.sites",
    'django.contrib.sitemaps',
    "django_htmx",
    'parler',
    'products',
    'sponsors',
    'blog',
]

UNFOLD = {
    "SITE_TITLE": "lulzcasz.dev",
    "SITE_HEADER": "Admin",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Blog",
                "icon": "article",
                "items": [
                    {"title": "Articles", "icon": "description", "link": "/admin/blog/article/"},
                    {"title": "Categories", "icon": "category", "link": "/admin/blog/category/"},
                    {"title": "Sections", "icon": "folder", "link": "/admin/blog/section/"},
                    {"title": "Tags", "icon": "tag", "link": "/admin/blog/tag/"},
                ],
            },
            {
                "title": "Products",
                "icon": "inventory_2",
                "items": [
                    {"title": "Products", "icon": "shopping_bag", "link": "/admin/products/product/"},
                    {"title": "Stores", "icon": "store", "link": "/admin/products/store/"},
                ],
            },
            {
                "title": "Sponsors",
                "icon": "handshake",
                "items": [
                    {"title": "Sponsors", "icon": "favorite", "link": "/admin/sponsors/sponsor/"},
                ],
            },
            {
                "title": "Users",
                "icon": "group",
                "items": [
                    {"title": "Users", "icon": "person", "link": "/admin/auth/user/"},
                    {"title": "Groups", "icon": "badge", "link": "/admin/auth/group/"},
                ],
            },
        ],
    },
    "COLORS": {
        "primary": {
            "50": "230 253 250",
            "100": "204 252 244",
            "200": "153 249 233",
            "300": "102 245 221",
            "400": "51 242 210",
            "500": "0 234 193",
            "600": "0 187 154",
            "700": "0 140 116",
            "800": "0 94 77",
            "900": "0 47 39",
            "950": "0 23 19",
        },
        "base": {
            "50": "250 250 250",
            "100": "244 244 245",
            "200": "228 228 231",
            "300": "212 212 216",
            "400": "161 161 170",
            "500": "113 113 122",
            "600": "82 82 91",
            "700": "63 63 70",
            "800": "31 28 27",
            "900": "16 16 16",
            "950": "9 9 11",
        },
    },
}

SITE_ID = 1

TAGGIT_CASE_INSENSITIVE = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{CELERY_BROKER_URL.rstrip('/')}/1", 
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

ROOT_URLCONF = 'lulzcasz_dev.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
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

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', "English"),
    ('pt-br', "Portuguese (Brazil)"),
)

PARLER_LANGUAGES = {
    1: (
        {'code': 'en'},
        {'code': 'pt-br'},
    ),
    'default': {
        'fallback': 'en',
        'hide_untranslated': True,
    }
}

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
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
AWS_S3_ADDRESSING_STYLE = os.getenv('AWS_S3_ADDRESSING_STYLE')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
