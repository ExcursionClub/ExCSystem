from ExCSystem.settings.base import *

MEDIA_ROOT = '/var/www/media/'
STATIC_ROOT = '/var/www/static/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DJANGO_DEBUG', False))
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': 5432
    }
}

# Email host settings
MEMBERSHIP_EMAIL_HOST_USER = os.environ.get('MEMBERSHIP_EMAIL_HOST_USER')
MEMBERSHIP_EMAIL_HOST_PASSWORD = os.environ.get('MEMBERSHIP_EMAIL_HOST_PASSWORD')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.1and1.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
# These two are used by the backend as the defaults
EMAIL_HOST_USER = MEMBERSHIP_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = MEMBERSHIP_EMAIL_HOST_PASSWORD


# Base address of where the page is available
WEB_BASE = "https://www.excursionclub.info"
SITE_DOMAIN = "www.excursionclub.info"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '%(levelname)s %(asctime)s [%(name)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'console_debug_false': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'console_debug_false'],  # , 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}