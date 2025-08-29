#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.
set -x  # Print commands and their arguments as they are executed.
export PYTHONUNBUFFERED=1 # Ensure Python output is unbuffered

echo "--- Running Migrations ---"
python manage.py migrate --noinput

echo "--- Collecting Static Files ---"
python manage.py collectstatic --noinput

echo "--- Creating Superuser (if not exists) ---"
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if username and email and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
END

echo "--- Starting Gunicorn ---"
gunicorn ecommerce.wsgi
