from uwccsystem.settings.base import *

DEBUG = bool(os.environ.get("DJANGO_DEBUG", True))

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

STATIC_URL = "static/"
MEDIA_URL = "media/"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "travis_ci_test",
        "USER": "foo",
        "PASSWORD": "bar",
        "HOST": "localhost",
        "PORT": 5432,
        "TEST": {"NAME": "travis_ci_test"},
    }
}

# Email host settings
EMAIL_HOST = "localhost"
EMAIL_PORT = 1024
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
