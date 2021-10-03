from uwccsystem.settings.base import *

DEBUG = True

STATIC_URL = "static/"
MEDIA_URL = "media/"

INSTALLED_APPS.extend([
    "minio_storage",
    "django_extensions"
])
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_STORAGE_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_STORAGE_ENDPOINT = os.environ.get("MINIO_STORAGE_ENDPOINT", "localhost:9000")
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = "media"
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_STATIC_BUCKET_NAME = "static"
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True
MINIO_STORAGE_STATIC_USE_PRESIGNED = True
MINIO_STORAGE_MEDIA_USE_PRESIGNED = True


CSRF_COOKIE_SECURE=False


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Email host settings
EMAIL_HOST = "localhost"
EMAIL_PORT = 1024
EMAIL_USE_TLS = False
MEMBERSHIP_EMAIL_NAME = "UWCC Membership"
MEMBERSHIP_EMAIL_HOST_USER = "membership@UWCCDev.org"
MEMBERSHIP_EMAIL_HOST_PASSWORD = ""
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Base address of where the page is available
WEB_BASE = "http://localhost:8000"

SITE_DOMAIN = "localhost:8000"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "standard": {
            "()": "django.utils.log.ServerFormatter",
            "format": "%(levelname)s %(asctime)s [%(name)s] %(message)s",
        }
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/default.log",
            "formatter": "standard",
        },
        "request_handler": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/requests.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "django.request": {
            "handlers": ["request_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
