# UWCCsystem [![Build Status](https://travis-ci.org/ExcursionClub/UWCCsystem.svg?branch=master)](https://travis-ci.org/ExcursionClub/UWCCsystem) [![Coverage Status](https://coveralls.io/repos/github/ExcursionClub/UWCCsystem/badge.svg?branch=master)](https://coveralls.io/github/ExcursionClub/UWCCsystem?branch=master) [![Maintainability](https://api.codeclimate.com/v1/badges/27d1df00c121f0e32ada/maintainability)](https://codeclimate.com/github/ExcursionClub/UWCCsystem/maintainability) 
Bottom up re-design of the Excursion system

#### Table of Contents
- [Getting Started](#getting-started)
    - Minimum setup to just get the project running
- [Development](#development)
    - Please read this before pushing any changes to git
- [Running Production](#run-in-production)
    - Quick, everyday tasks to maintain the productions server
- [Scheduled Tasks](#scheduled-tasks)
    - Reference for automatic recurring tasks in production
- [AWS deployment](#aws-deployment)
    - Reference for how the real production server is setup


## Getting Started
We use Heroku to host our app. The dev branch will automatically be deploy [here](https://excsystem.herokuapp.com/) and the master [here](https://excsystem-prod.herokuapp.com/).

### Install
Local development requires [python3.8](https://www.python.org/downloads/release/python-381/), [Pipenv](https://github.com/pypa/pipenv/), [Docker](https://www.docker.com/) and [Minio](https://github.com/minio/minio).

#### macOS
Install [Postgres.app](https://postgresapp.com/)
```
$ brew install postgresql
```

Add the pg_config to `$PATH`:
```
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
```

#### Both
Setup local object storage. The file uploaded here are not persistent and will disappear when the container is closed. 
```
$ docker run -p 9000:9000 --name minio1 \
  -e "MINIO_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE" \
  -e "MINIO_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
  minio/minio server /data
```

Get the latest version of the code from git:
```bash
git clone git@github.com:TomekFraczek/UWCCsystem.git 
cd UWCCsystem/
```

Use pipenv to install all dependencies used by the development version:
```bash
$ pipenv install --dev && pipenv shell
```

Set environment variables:
```bash
# Tell the server whether to run 'development' mode (all changes are local so you can break anything and not worry)
export ENV_CONFIG=development

# Create a password for test users
export PASSWORD=

# Tell the system how to connect to minio
export MINIO_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
export MINIO_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

You're now ready to run the test server
```bash
$ python manage.py collectstatic
$ ENV_CONFIG="development"; python manage.py runserver
```

Tada! You should have gotten a prompt that the server is now running. Just go to http://127.0.0.1:8000 to see!

### Emails
Several parts of the project send out emails (i.e. when creating a new user). These processes will generally 
crash if an email server is not set up. For setup of the production email server, see the deployment section below. 
During development however, we currently use the console email backend to print the emails to the console.


## Development
### Linting
This codebase uses the PEP 8 code style. We enforce this with Black.
```bash
$ black . --exclude venv
```

We use type hints to statically check types. These are optional, but serves as up-to-date documentation and can catch errors in deeply nested objects. Check a file by running
```bash
$ mypy . --ignore-missing-imports
```

### Unit Tests
TravisCI will run tests on all PRs.

To run tests locally:

```bash
$ python3 manage.py test
```

### Test Coverage
Generate reports to inspect test coverage line-by-line

```bash
$ coverage run manage.py test whatever -v 2
$ coverage html
```

### Functional Tests
Install geckodriver and Firefox

Django has to be running to test with selenium. Run these two commands in different windows:
```bash
$ python manage.py runserver
$ python3 functional_tests.py
```

### Applying Changes to the Models
Most changes to the code will be incorporated into the website immediately.
The exception to this rule are any changes to the models that affect how data is stored in the database.
To incorporate these, stop the server, and run:

```bash
$ python3 manage.py makemigrations <app_name>
$ python3 manage.py migrate
```

It's important to run create small atomic migrations to make it easy to roll back if we mess up our database.
So specify the app and don't run huge migrations.
This should be sufficient for small changes that do not cause conflicts.
However if it does it means that the data in the database can't satisfy the new constraints.
E.g. create a migrations that sets a field to be not null and that field is null for a record in the database.
If an error pops up, and there is not important information in the
database, you can reset the database (see below).

### Resetting the Database
If you at any point make a significant change to how data is stored in
the database, chances are that you will run into migration conflicts
when running the `makemigrations` and `migrate` commands. In the early
stages, you can safely and easily reset the entire database from scratch
using the ResetDatabase.py file.

To restart the database:

```bash
$ python3 task.py reset_database
$ python3 task.py populate_database
```

This will wipe everything that exists in the database, and generate random data for the new database.

The server is now set up, and ready to run as if this was the first time
ever running the project, though with the database populated with dummy data. Running `populate_database.py` twice won't work as it tries to add users with the same RFID and that would violate the unique constraints on the database.

NOTE: **NEVER** push your dev database or migrations to the repository. The only migrations that should ever be pushed are 
those that are intended to be applied on the production server.


## Heroku
Reset DB
```bash
$ heroku pg:reset DATABASE_URL --app APP_NAME
$ heroku run python manage.py migrate --app APP_NAME
$ heroku run python tasks.py populate_database --app APP_NAME
```


## Run in production
It is often necessary to run updates and basic maintainence on the server. This section explains how this should be done.

#### Run checklist
Before you run the server it's advisable that you make sure all the following are true:
- All packages are up to date
  ```bash
  sudo apt update
  sudo apt upgrade
  ```
- You are executing commands from the UWCCsystem directory
  ```bash
  cd ~/UWCCsystem
  ```
- You have the newest version of the code
  ```bash
  git checkout master
  git pull
  ```
- You are set to run with production settings (```echo $ENV_CONFIG``` gives ```production```)
- All your environment variables are set with the newest values ([Environment Variables](#environment-variables))
- All python packages are installed correctly (run  ```pipenv install```)
- Migrate the database ([Prepare Database](#prepare-database))
- Collect static files ([Create folders for static files](#create-folders-for-static-files))

#### Boot and Reboot:
To run the server on the production machine first kill the old python process
```bash
$ ps -ef | grep python
ubuntu    7339  7220  0 07:01 pts/0    00:00:00 python3 -m pipenv shell
$ kill -9 7339
```

Then remember to activate the virtual environment before starting the server
```bash
$ pipenv shell
$ nohup python manage.py runserver &
```
This will run Django in the background, even after you exit your SSH session.
('fg' brings process to current shell)

For convenience, you can easily reboot the server using ```./rebootServer.sh```
It is also useful to periodically reboot the AWS server itself with ```sudo reboot```

#### Monitoring status
The server is connected to Sentry, which logs all errors online and sends notifications to the 'verybadbugs' channel in 
Slack. 

All server output is stored in logs in the 'logs' directory. Debug stores all output in significant detail, requests 
stores a list of all requests made to the server.

Current server output is redirected via nohup, and can be followed with:
```bash
$ tail -f nohup.out
```
Exit by pressing Ctrl+C



## Scheduled tasks
There are certain scheduled tasks which are run automatically and periodically. Currently we use ```crontab``` to manage
scheduling. Tasks should be run through a ```tasks.py``` in each app in the system. 

#### How to change scheduling
To edit the scheduling, simply ssh into the server and run:
```bash
$ crontab -e
``` 
This will open the scheduling file in ```vi```. These links give you more information on how to use 
[vi](https://www.openvim.com/) and [crontab](https://crontab.guru).

### Current Tasks

This is a list of all the currently scheduled tasks. Please keep this as up to date as you can!

- Expire Members
    - Command: ```python core/tasks.py expireMembers```
    - Should be run once a day, preferably in the evening/night
    - This task goes through all the active members in the database and sets all those whose expiration data has passed to
    be in the 'expired' group. Additionally any members who will expire in a week are sent a warning email that they 
    will soon expire.
- Update Listserv
    - Command ```python core/tasks.py updateListserv```
    - Should be run at least once a week, shortly before the general email is sent out
    - This tasks collect all the emails of all members with an active membership (in groups 'Member', 'Staff' or 
    'Board'), saves these to a text file, and uploads this file to the listserv


## AWS Deployment
This section is a reference for how the production server and database are set up. Hopefully it will never need to be 
used to re-construct things from scratch, but in case it does, please keep this up to date!

Start by launching an EC2 instance with Ubuntu 18.04. Use the free tier. SSH into the instance.
For help on how to do this look [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html).

#### Upgrade packages and install dependencies
```bash
$ sudo apt-get update
$ sudo apt-get upgrade -y
$ sudo apt-get install python3 nginx libpq-dev python3-dev postgresql postgresql-contrib  -y
$ curl https://raw.githubusercontent.com/kennethreitz/pipenv/master/get-pipenv.py | python
```

### Nginx config
Access to the django server is handled by nginx to ensure proper distribution of requests. 
Ensure that nginx is installed. If you run it, it should create a config file in: ```/etc/nginx/conf.d```

Replace the server block in the config file with:
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

To now run nginx so that it's ready to handle the django server:
```bash
$ sudo nginx -t
$ sudo service nginx reload
```
This should cause nginx to run whenever the AWS server is booted, but if you run into trouble always check that nginx is
up and running.


#### Add SSL
Install packages for python/nginx to automatically manage the SSL certificates so that we can use HTTPS
```bash
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get update
$ sudo apt-get install python-certbot-nginx 
```

#### Update AWS security groups to enable HTTP traffic
Add HTTP and HTTPS rule: set ports 80 and 443 to be open to incoming traffic from anywhere. If this is not done web 
requests will never actually reach the server. 

### Postgres
Use RDS to create a free-tier Postgres instance. This will also create a default database.

Since the database is on a different server than the app, it needs a more describing name. Something like this: `excursion.xho0gsojfppx.us-east-1.rds.amazonaws.com`

Connect to the database with psql from the EC2 instance. This way you don't have to open the network to the outside world.
You can easily do this by executing the script: 
`./openPostgresDB.sh`

To set up the database to be ready for use by the system:
```bash
$ sudo -su postgres
$ createuser --interactive -P
```

Now fill out the prompts you receive as below
```
Enter name of role to add: admin
Enter password for new role:
Enter it again:
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) y
Shall the new role be allowed to create more new roles? (y/n) n
```

To create the actual database used by the system
```bash
createdb --owner admin uwccsystem
psql
grant ALL ON database uwccsystem to admin;
```


### App setup
You are now ready to run the server so that all your hard work hereto will be useful.

Get the latest version of the code from the repository. If you are creating a new instance run:
```bash
git clone https://github.com/TomekFraczek/UWCCsystem.git
cd UWCCsystem
```
If you already have a git repository with the code, ensure you are on the master branch and pull the newest version of 
the code:
```bash
$ git checkout master
$ git pull
```

Now ensure that all the packages used in the project are installed and ready:
```bash
$ pipenv install --deploy --system
```

Note: If you ever run into issues where the wrong version of python is trying to run, you can update the symlink:
```bash
$ sudo rm /usr/bin/python3
$ sudo ln -s /usr/bin/python3 /usr/bin/python3
```

```bash
# Generate keys:
$ python3 manage.py shell -c 'from django.core.management import utils; print(f"export SECRET_KEY=\"{utils.get_random_secret_key()}\"")' >> ~/.profile
```
#### Environment Variables
All the below variables must be set with the appropriate values (from the above configuration process). None of these 
values should ever be shared publicly as they would give anyone access to the server internals. If you need to know 
these values, please look on slack or ask one of the admins.
```bash
# Tell the server whether to run in 'production' or 'development'
export ENV_CONFIG=production

# Login data to the database
export POSTGRES_USER=ex
export POSTGRES_PASSWORD=
export POSTGRES_HOST=
export POSTGRES_DB_NAME=

# Login data to the email server(s)
export MEMBERSHIP_EMAIL_HOST_USER=
export MEMBERSHIP_EMAIL_HOST_PASSWORD=

# Tell the storage backend how to  connect to Amazon S3
export AWS_ACCESS_KEY_ID= 
export AWS_SECRET_ACCESS_KEY=
export AWS_STORAGE_BUCKET_NAME =

# Host identifiers for security and address building
export NGINX_HOST_IP=
export NGINX_HOST_DNS=
export HOST_NAMESPACE=

```
To make the environment variables persist through sessions, you can put the above export statements in the file `~/.bash_profile`

#### Prepare Database
For django to be able to store data, we need to create the database schema. to do this run:
```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

To populate the database with start data (groups, permissions, quiz questions etc) run:
```bash
$ python3 build_basic_data.py
```

#### Create folders for static files
Static and media files for the production server are stored in an S3 bucket. 

To make sure the server is getting access to s3, ensure the above environment variables are set and run:
```bash
$ ENV_CONFIG=production; python3 manage.py collectstatic
```

Everything should now be set up correctly. Check out [Run in Production](#run-in-production) for info on how to run the
server.
