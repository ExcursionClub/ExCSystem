ExCSystem
---------

Bottom up re-design of the Excursion system
________________
<b>Install</b>

This project runs on python 3.5!

To install simply install the latest version of django, and any
dependencies:
   * Django 1.11.5
   * django-phonenumber-field
   * names
   * progressbar2

Then clone the git repo anywhere

_____________________
<b>Running</b>

To run the server, simply navigate to the top ExCSystem directory (the
one with manage.py in it) and run

    python3.5 manage.py runserver
    
The website is now available at http://127.0.0.1:8000 and the admin panel is at http://127.0.0.1:8000/admin
    
 _____________________
<b>General Function</b>

This project is, as it is written in Django, very much database-driven. It's focus to provide a
simple, easy to use, understand, and extend interface for the databases that are the backbone of 
the Excursion Club rental system. To do so there are three main data models/tables.

<u>Member</u>:
    These are the members of the excursion club. If the member is also a staffer, they have staffer exclusive
    data saved via the proxy model Staffer.
    
<u>Gear</u>:
    These are all the things at the excursion club that can potentially be rented. No changes should ever
    be made by modifying the data on a piece of gear directly.
    
<u>Transaction</u>:
    The most powerful of the three, transactions are a type of log of all the changes to the gear
    data. Most importantly however, <b> creating a transaction modifies the gear table in the corresponding 
    way </b>. Therefore, by analyzing the transaction history, the exact state of any piece of gear can be 
    determined.
    
The kiosk module is intended to provide an clean and easy to use interface for creating and modifying transactions.
The automatically generated Django admin panel serves as a method to view and edit certain data. The exact 
functionality depends on the permission level of the user.

<u>Member</u>:
    Can only see the types of gear that are available, but cannot see the exact quantities or make any changes

<u>Staffer</u>:
    Can see exactly what gear is available, and can make basic changes to members

<u>Board Member</u>:
    Is allowed to make any modifications to members.

<u>Admin</u>:
    There should only ever be one admin, this user can arbitrarily modify any element of the database except 
    Transactions and Gear. Any change to gear must be made through the admin override transaction
    
_____________________
<b>Applying Changes</b>

Most changes to the code will be incorporated into the website
immediately. The exception to this rule are any changes to the models
that affect how data is stored in the database. To incorporate these,
stop the server, and run:

    python3.5 manage.py makemigrations core
    python3.5 manage.py migrate

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

    python3.5 RestartDatabase.py
    python3.5 PopulateDatabase.py

This will wipe everything that exists in the database, and generate random data for the new database

The server is now set up, and ready to run as if this was the first time
ever running the project, though with the database populated with dummy data

NOTE: Neither the database, nor anything in the migrations directory
should ever be pushed to the git repo. The migrations directory on the
 git repo is intentionally there and empty to simplify initial setup.