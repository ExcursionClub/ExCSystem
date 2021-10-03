"""File that sets up the django environment. Must be called at the beginning of any django script"""
import os
import django

print(f"Setting up django with {os.environ.get('ENV_CONFIG')} settings")
if os.environ.get("ENV_CONFIG") == "development":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uwccsystem.settings.development")
elif os.environ.get("ENV_CONFIG") == "ci":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uwccsystem.settings.ci")
elif os.environ.get("ENV_CONFIG") == "staging":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "excsystem.settings.staging")
elif os.environ.get("ENV_CONFIG") == "prod2":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "excsystem.settings.prod2")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uwccsystem.settings.production")

django.setup()
