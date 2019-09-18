"""
This script removes all traces of the old database and sets up a new one,
so that the server can be run clean
"""

import os
import shutil

import django

# Re-initializes the database
from django.core.management import call_command

# Prepares the necessary paths
basepath = os.getcwd()

# Prepares python to be able to run django commands
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uwccsystem.settings.development")
django.setup()
try:
    os.remove(os.path.join(basepath, "db.sqlite3"))
except FileNotFoundError:
    print("The database does not exist. Moving on...")


# Re-creates __init__.py in the migrations folder
call_command("migrate")

# To finish setup, run the following from the command line:
# python3.5 manage.py createsuperuser --email=admin@climbingclubuw.org --rfid=0000000000
# --first_name=Master --last_name=admin --phone_number=+15555555555
