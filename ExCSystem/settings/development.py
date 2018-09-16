from ExCSystem.settings.base import *


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MEDIA_URL = '/media/'

# Email host settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1024

# Base address of where the page is available
WEB_BASE = "http://127.0.0.1:8000"
