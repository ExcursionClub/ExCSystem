import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


MEDIA_URL = "/media/"
DEFAULT_IMG = "uwcclogo.png"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "=ypf2)!((#kx_+$l6ahx-j=_tf-sl=%vaw-u@fjl25x%)=mrj*"
)

SITE_ID = 1
SITE_NAME = "Climbing Club System"
CLUB_EMAIL = '@climbingclubuw.org'

GEAR_EXPIRE_TIME = timedelta(days=90)

ALLOWED_HOSTS = ["*"]

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

INSTALLED_APPS = [
    "core",
    "frontpage",
    "kiosk",
    "api",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    'django_user_agents',
    "phonenumber_field",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = "uwccsystem.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "core/templates"),
            os.path.join(BASE_DIR, "frontpage/templates"),
            os.path.join(BASE_DIR, "kiosk/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "uwccsystem.wsgi.application"

AUTH_USER_MODEL = "core.Member"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

PHONENUMBER_DB_FORMAT = "INTERNATIONAL"
PHONENUMBER_DEFAULT_FORMAT = "INTERNATIONAL"
PHONENUMBER_DEFAULT_REGION = "US"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Pacific"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "kiosk:home"
LOGOUT_REDIRECT_URL = "front-page:home"

LISTSERV_USERNAME = os.environ.get("LISTSERV_USERNAME")
LISTSERV_PASSWORD = os.environ.get("LISTSERV_PASSWORD")
LISTSERV_FORM_ADDRESS = os.environ.get("LISTSERV_FORM_ADDRESS")
