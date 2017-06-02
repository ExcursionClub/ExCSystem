"""
This script removes all traces of the old database and sets up a new one, so that the server can be run clean
"""


import os
import shutil
import django


# Prepares the necessary paths
basepath = os.getcwd()
migrations_path = os.path.join(basepath, 'core', 'migrations')


# Prepares python to be able to run django commands
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ExCSystem.settings")
django.setup()


# Removes all the migration files and the entire database
try:
    shutil.rmtree(migrations_path)
except FileNotFoundError:
    print("migrations file does not exist. Moving on...")
try:
    os.remove(os.path.join(basepath, 'db.sqlite3'))
except FileNotFoundError:
    print("The database does not exist. Moving on...")
print("a")

# Re-creates __init__.py in the migrations folder
os.mkdir(migrations_path)
open(os.path.join(migrations_path, '__init__.py'), 'w')


# Re-initializes the database
from django.core.management import call_command
print("b")
call_command('makemigrations', 'core')
call_command('migrate')
print("c")
call_command('createsuperuser', '--username', 'admin', '--email', 'admin@excursionclubucsb.org')




