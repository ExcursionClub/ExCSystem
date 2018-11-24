from ExCSystem.settings.base import *

DEBUG = True

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_STORAGE_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
MINIO_STORAGE_ENDPOINT = os.environ.get('MINIO_STORAGE_ENDPOINT', "localhost:9000")
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = "media"
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_STATIC_BUCKET_NAME = "static"
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True
MINIO_STORAGE_STATIC_USE_PRESIGNED = True

STATIC_URL = 'static/'

"""
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = os.environ.get('AWS_LOCATION')

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
"""




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Email host settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1024
MEMBERSHIP_EMAIL_HOST_USER = 'membership@ExCDev.org'
MEMBERSHIP_EMAIL_HOST_PASSWORD = ''
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Base address of where the page is available
WEB_BASE = "http://localhost:8000"
SITE_DOMAIN = "localhost:8000"

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
        'standard': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '%(levelname)s %(asctime)s [%(name)s] %(message)s',
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/default.log',
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/requests.log',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
