# Social Network API

This is a social networking API built using Django Rest Framework. The API supports user registration, login, searching for users by email, sending/accepting/rejecting friend requests, listing friends, and listing pending friend requests.

## Features

- User Registration and Login
- User Authentication with Token
- Search Users by Email
- Send/Accept/Reject Friend Requests
- List Friends
- List Pending Friend Requests
- Prevent sending more than 3 friend requests within a minute
- Case-insensitive email handling

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized setup)

### Clone the Repository

```bash
git clone https://github.com/manishp042/social_network.git
cd social_network
```

### Set Up a Virtual Environment
- python -m venv venv
- source `venv/bin/activate`  # On Windows use `venv\Scripts\activate`

### Install Dependencies   
- pip install -r requirements.txt

### Apply Migrations
- python manage.py makemigrations
- python manage.py migrate

### Create a Superuser
- python manage.py createsuperuser

### Run the Development Server
- python manage.py runserver

The API will be available at `http://localhost:8000`


# Docker Setup 
### Update Django Settings:
- Update your settings.py to use the environment variables for the database configuration:

```bash import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```
## Running the Docker Containers

1.) Build and Run the Containers:
```bash
docker-compose up --build
```
2.) Apply Migrations:
```bash 
docker-compose exec web python manage.py migrate
```

3.) Create a Superuser:
```bash 
docker-compose exec web python manage.py createsuperuser
```


The API should now be available at http://localhost:8000.

### Summary
The provided Dockerfile and docker-compose.yml will set up a Docker environment for your Django project with a PostgreSQL database. The Django application will run inside a Docker container and connect to the PostgreSQL database, which is also running inside a Docker container.

Make sure to adjust the environment variables and settings as needed for your specific use case.