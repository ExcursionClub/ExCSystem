from ExCSystem.settings.base import *


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Email host settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1024

