"""File that sets up the django enviroment. Must be called at the beginning of any django script"""
import os

import django

print(f"Setting up django with {os.environ.get('ENV_CONFIG')} settings")
if os.environ.get("ENV_CONFIG") == "development":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExCSystem.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExCSystem.settings.production')

django.setup()
