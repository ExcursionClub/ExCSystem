# ExCSystem

Bottom up re-design of the Excursion system

## Getting Started

This project requires python3.5 and virtualenv.

```bash
$ git clone git@github.com:TomekFraczek/ExCSystem.git && cd ExCSystem/
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python manage.py runserver
```

## Applying Changes</b>

Most changes to the code will be incorporated into the website
immediately. The exception to this rule are any changes to the models
that affect how data is stored in the database. To incorporate these,
stop the server, and run:

```bash
python3.5 manage.py makemigrations core
python3.5 manage.py migrate
```

This should be sufficient for small changes that do not cause conflicts.
If an error pops up, and there is not important information in the
database, you can reset the database (see below).

## Resetting the Database

If you at any point make a significant change to how data is stored in
the database, chances are that you will run into migration conflicts
when running the `makemigrations` and `migrate` commands. In the early
stages, you can safely and easily reset the entire database from scratch
using the ResetDatabase.py file.

To restart he database:

```bash
python3.5 RestartDatabase.py
python3.5 PopulateDatabase.py
```

This will wipe everything that exists in the database, and generate random data for the new database

The server is now set up, and ready to run as if this was the first time
ever running the project, though with the database populated with dummy data

NOTE: Neither the database, nor anything in the migrations directory
should ever be pushed to the git repo. The migrations directory on the
 git repo is intentionally there and empty to simplify initial setup.
