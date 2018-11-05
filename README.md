# ExCSystem [![Build Status](https://travis-ci.org/ExcursionClub/ExCSystem.svg?branch=master)](https://travis-ci.org/ExcursionClub/ExCSystem) [![Maintainability](https://api.codeclimate.com/v1/badges/27d1df00c121f0e32ada/maintainability)](https://codeclimate.com/github/ExcursionClub/ExCSystem/maintainability) 
Bottom up re-design of the Excursion system

## Getting Started
This project requires python3.7 and Pipenv.

### Install
```bash
$ git clone git@github.com:TomekFraczek/ExCSystem.git && cd ExCSystem/
$ pipenv install --dev
$ pipenv shell
$ ENV_CONFIG="development"; python3 manage.py runserver
```

### Emails
Several parts of the project send out emails (i.e. when creating a new user). These processes will generally 
crash if an email server is not set up. For setup of the production email server, see the deployment section below. 
During development however, we currently use the console email backend to print the emails to the console.


## Development
### Linting
Use type hints to statically check types. These are optional, but serves as up-to-date documentation and can catch errors in deeply nested objects. Check a file by running
```bash
$ mypy <file> --ignore-missing-imports
```

This codebase uses the PEP 8 code style. We enforce this with isort, yapf & flake8.
In addition to the standards outlined in PEP 8, we have a few guidelines
(see `setup.cfg` for more info):
We use type hints to statically check types. These are optional, but serves as up-to-date documentation and can catch errors in deeply nested objects. Check a file by running
```bash
$ mypy <file> --ignore-missing-imports
$ flake8 <file>
$ isort <file>
$ yapf -i <file>
```

### Unit Tests
TravisCI will run tests on all PRs.

To run tests locally:

```bash
$ python3.7 manage.py test
```

### Functional Tests
Install geckodriver and Firefox

Django has to be running to test with selenium. Run these two commands in different windows:
```bash
$ python manage.py runserver
$ python3.7 functional_tests.py
```

## Applying Changes to the Models</b>
Most changes to the code will be incorporated into the website immediately.
The exception to this rule are any changes to the models that affect how data is stored in the database.
To incorporate these, stop the server, and run:

```bash
$ python3.7 manage.py makemigrations <app>
$ python3.7 manage.py migrate
```

It's important to run create small atomic migrations to make it easy to roll back if we mess up our database.
So specify the app and don't run huge migrations.
This should be sufficient for small changes that do not cause conflicts.
However if it does it means that the data in the database can't satisfy the new constraints.
E.g. create a migrations that sets a field to be not null and that field is null for a record in the database.
If an error pops up, and there is not important information in the
database, you can reset the database (see below).

## Resetting the Database
If you at any point make a significant change to how data is stored in
the database, chances are that you will run into migration conflicts
when running the `makemigrations` and `migrate` commands. In the early
stages, you can safely and easily reset the entire database from scratch
using the ResetDatabase.py file.

To restart the database:

```bash
$ python3.7 RestartDatabase.py
$ python3.7 PopulateDatabase.py
```

This will wipe everything that exists in the database, and generate random data for the new database.

The server is now set up, and ready to run as if this was the first time
ever running the project, though with the database populated with dummy data. Running `PopulateDatabase.py` twice won't work as it tries to add users with the same RFID and that would violate the unique contstraint on the database.

NOTE: Neither the database, nor anything in the migrations directory
should ever be pushed to the git repo. The migrations directory on the
 git repo is intentionally there and empty to simplify initial setup.

## AWS Deployment
Start by launching an EC2 instance with Ubuntu 18.04. Use the free tier. SSH into the instance

### Upgrade packages and install dependencies
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install python3.7 nginx libpq-dev python3.7-dev postgresql postgresql-contrib  -y
curl https://raw.githubusercontent.com/kennethreitz/pipenv/master/get-pipenv.py | python
```

### Nginx config
Remove the server block in nginx.conf`

Create a conf file in /etc/nginx/conf.d
```
server {

  listen 80;
  listen 443 ssl;
  # Type your domain name below
  server_name excursionclub.info www.excursionclub.info;

# Always serve index.html for any request
  location / {
      proxy_pass http://localhost:8000;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
  }
  location /static/ {
      alias   /var/www/static/;
  }

  location /media/ {
      alias   /var/www/media/;
  }

  location /admin/ {
    proxy_pass http://localhost:8000/admin/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
  }
}
```

Then run
```bash
sudo nginx -t
sudo service nginx reload
```

### Add SSL
```bash
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx 
```

### Update AWS security groups to enable HTTP traffic
Add HTTP and HTTPS rule

### Postgres
Use RDS to create a free-tier Postgres instance. This will also create a default database.

Since the database is on a different server than the app, it needs a more describing name. Something like this:
The hostname `excursion.xho0gsojfppx.us-east-1.rds.amazonaws.com`

Connect to the database with psql from the EC2 instance. This way you don't have to open the network to the outside world.
You can easily do this by executing the script: 
`./openPostgresDB.sh`

Local
```bash
sudo -su postgres
createuser --interactive -P

###
# If you need to delete the db run:
psql
drop database excsystem;
create database excsystem;
grant ALL ON database excsystem to admin;
###

sudo -su postgres
createuser --interactive -P
Enter name of role to add: admin
Enter password for new role:
Enter it again:
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) y
Shall the new role be allowed to create more new roles? (y/n) n

createdb --owner admin excsystem
psql
grant ALL ON database excsystem to admin;
```

### App setup
```bash
# Update symlink to point to Python3.7
sudo rm /usr/bin/python3
sudo ln -s /usr/bin/python3.7 /usr/bin/python3

git clone https://github.com/ExcursionClub/ExCSystem.git
cd ExCSystem
pipenv install --deploy --system

# Generate keys:
python3.7 manage.py shell -c 'from django.core.management import utils; print(f"export SECRET_KEY=\"{utils.get_random_secret_key()}\"")' >> ~/.profile

# Login data to the database
export POSTGRES_USER=ex
export POSTGRES_PASSWORD=
export POSTGRES_HOST=
export POSTGRES_DB_NAME=

# Login data to the email server(s)
export MEMBERSHIP_EMAIL_HOST_USER=
export MEMBERSHIP_EMAIL_HOST_PASSWORD=

# Tell the server whether to run in 'production' or 'development'
export ENV_CONFIG=production

# Tell celery how to  connect to Amazon SQS
export AWS_ACCESS_KEY_ID= 
export AWS_SECRET_ACCESS_KEY=

python3.7 manage.py makemigrations
python3.7 manage.py migrate
```
To make the environment variables persist through sessions, you can put the above export statements in the file `~/.bash_profile`

To populate the database with start data (groups, permissions, quiz questions etc) you can run:
```bash
python3.7 buildBasicData.py
```

### Create folders for static files
Linux
```bash
# Location?
sudo chown ec2-user:ec2-user /var/www/static/ /var/www/media/
python3.7 manage.py collectstatic
```

# Ubuntu
This only needs to be done once per instance
```bash
sudo mkdir /var/www/static
sudo mkdir /var/www/media
sudo chown ubuntu:ubuntu /var/www/static/ /var/www/media/
python3.7 manage.py collectstatic
```

### Run in production
```bash
nohup ENV_CONFIG="production"; python3.7 manage.py runserver &
This will run Django in the background, even after you exit your SSH session.
('fg' brings process to current shell)
```
Note: Crontab (automatic linux scheduling utility) is configured to run this command whenever the server is rebooted

This project also includes several tasks that run periodically and are managed by celery. To enable celery:
```bash
celery -A ExCSystem beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
