# ideas-graphql-api
Ideary - An app to share your ideas

# Virtual enviroment

## Create a Python3 virtual enviroment (Developed in Python 3.8.10)

    virtualenv venv -p python3

## Activate it and install dependencies

    source venv/bin/activate
    pip install -r requirements

# Database - Postgres

## Run Postgres docker

Navigate to postgres docker-compose file, change the example password  to a `<new_safe_password>` and run it

    cd config/docker/postgresql
    docker-compose up -d

## Create database and user

First connect to postgres using the default user `postgres` and `<new_safe_pasword>`

    psql -h localhost -p 5432 -U postgres
Now let's create database, user (with password) and give permissions. In the settings example we use `ideary_db`, `ideary_user` and `4f5TFGT*5*YysJ`. It's recommended to change them (you need to update also `settings.py` file)

    create database ideary_db;
    create user ideary_user with encrypted password '4f5TFGT*5*YysJ';
    grant all privileges on database ideary_db to ideary_user;
You can exit postgres console now.

# Run migrations
Run django migrations to set up the database

    python manage.py migrate
