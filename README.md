ExCSystem
---------

Bottom up re-design of the Excursion system
________________
<b>Install</b>

This project runs on python 3.4!

To install simply install the latest version of django, and any
dependencies:
   * none

Then clone the git repo anywhere

_____________________
<b>Running</b>

To run the server, simply navigate to the top ExCSystem directory (the
one with manage.py in it) and run

    python3.4 manage.py runserver

_____________________
<b>Resetting the Database</b>

If you at any point make a significant change to how data is stored in
the database, chances are that you will run into migration conflicts
when running the 'makemigrations' and 'migrate' commands. In the early
stages, you can safely and easily reset the entire database from scratch
using the ResetDatabase.py file.

To restart he database:

    python3.4 RestartDatabase.py
    python3.4 manage.py createsuperuser --username=admin --email=admin@excursionclubucsb.org

You will now be prompted to enter a password for the super user.
Enter whatever you like, ie admin


The server is now set up, as if this was the first time ever running the
project.

NOTE: Neither the database, nor anything in the migrations directory
should ever be pushed to the git repo. The migrations directory on the
 git repo is intentionally there and empty to simplify initial setup.