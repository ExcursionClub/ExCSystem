"""File that sets up the django enviroment. Must be called at the beginning of any django script"""
import os

import django

print(f"Setting up django with {os.environ.get('ENV_CONFIG')} settings")
if os.environ.get("ENV_CONFIG") == "development":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "excsystem.settings.development")
elif os.environ.get("ENV_CONFIG") == "ci":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "excsystem.settings.ci")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "excsystem.settings.production")

django.setup()
