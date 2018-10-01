"""File that sets up the django enviroment. Must be called at the beginning of any django script"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExCSystem.settings.production')
django.setup()
