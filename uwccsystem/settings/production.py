import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from uwccsystem.settings.base import *

sentry_sdk.init(
    dsn="https://e9f3e4184b1e4ef09bf56624163e6d83@sentry.io/1726068",
    integrations=[DjangoIntegration()])

STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_FILE_STORAGE = "uwccsystem.settings.storage_backends.MediaStorage"

MEDIA_ROOT = "/var/www/media/"
STATIC_ROOT = "/var/www/static/"

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_LOCATION = os.environ.get("AWS_LOCATION")

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"


CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DJANGO_DEBUG", False))
ALLOWED_HOSTS = [os.environ.get("HOST_NAMESPACE"), os.environ.get("NGINX_HOST_IP"), os.environ.get("NGINX_HOST_DNS")]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": 5432,
    }
}

# Email host settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = os.environ.get("EMAIL_HOST")
# EMAIL_USE_TLS = True
# EMAIL_PORT = os.environ.get("EMAIL_PORT")
# These two are used by the backend as the defaults
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_API_KEY = os.environ.get("EMAIL_API_KEY")

EMAIL_DEFAULT_NAME = 'Climbing Club at UW'
EMAIL_DEFAULT = f'info{CLUB_EMAIL}'

MEMBERSHIP_EMAIL_NAME = 'CCUW Membership'
MEMBERSHIP_EMAIL = f'membership{CLUB_EMAIL}'

# Tells celery we will use Amazon SQS, interpets rest from env variables
BROKER_URL = "sqs://"

# Base address of where the page is available
WEB_BASE = f"https://www{os.environ.get('HOST_NAMESPACE')}"
SITE_DOMAIN = f"www{os.environ.get('HOST_NAMESPACE')}"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "%(levelname)s %(asctime)s [%(name)s] %(message)s",
        }
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/debug.log",
            "formatter": "django.server",
        },
        "request_handler": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/requests.log",
            "formatter": "django.server",
        },
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "console_debug_false": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "django": {"handlers": ["console", "console_debug_false"], "level": "INFO"},
        "django.request": {
            "handlers": ["request_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
