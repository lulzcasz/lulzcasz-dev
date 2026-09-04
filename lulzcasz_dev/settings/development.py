from .base import *

DEBUG = True

INTERNAL_IPS = ["127.0.0.1", "localhost"]

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

AWS_S3_URL_PROTOCOL = "http:"
