from .base import *

DEBUG = True

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

AWS_S3_URL_PROTOCOL = "http:"
