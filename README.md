ExCSystem
---------

Bottom up re-design of the Excursion system
________________
<b>Install</b>

This project runs on python 3.4!

To install simply install the latest version of django, and any
dependencies:
   * Django 1.11.2
   * django-phonenumber-field

Then clone the git repo anywhere

_____________________
<b>Running</b>

To run the server, simply navigate to the top ExCSystem directory (the
one with manage.py in it) and run

    python3.4 manage.py runserver

_____________________
<b>Applying Changes</b>

Most changes to the code will be incorporated into the website
immediately. The exception to this rule are any changes to the models
that affect how data is stored in the database. To incorporate these,
stop the server, and run:

    python3.4 manage.py makemigrations core
    python3.4 manage.py migrate

This should be sufficient for small changes that do not cause conflicts.
If an error pops up, and there is not important information in the
database, you can reset the database (see below).


_____________________
<b>Resetting the Database</b>

If you at any point make a significant change to how data is stored in
the database, chances are that you will run into migration conflicts
when running the 'makemigrations' and 'migrate' commands. In the early
stages, you can safely and easily reset the entire database from scratch
using the ResetDatabase.py file.

To restart he database:

    python3.4 RestartDatabase.py
    python3.4 manage.py createsuperuser --email=admin@excursionclubucsb.org --rfid=0000000000 --first_name=Master --last_name=Admin --phone_number=+15555555555

You will now be prompted to enter a password for the super user.
Enter whatever you like, ie admin


The server is now set up, and ready to run as if this was the first time
ever running the project.

NOTE: Neither the database, nor anything in the migrations directory
should ever be pushed to the git repo. The migrations directory on the
 git repo is intentionally there and empty to simplify initial setup.