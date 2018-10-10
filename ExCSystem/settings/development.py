from ExCSystem.settings.base import *


DEBUG = True

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

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
