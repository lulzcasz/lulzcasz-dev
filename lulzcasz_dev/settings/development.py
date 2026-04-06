from .base import *

DEBUG = True

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

AWS_S3_URL_PROTOCOL = "http:"

HOST_PORT = '8000'
HOST_SCHEME = 'http'
