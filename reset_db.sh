./venv/bin/python manage.py reset_db --noinput
./venv/bin/python manage.py migrate --noinput
DJANGO_SUPERUSER_PASSWORD=admin ./venv/bin/python manage.py createsuperuser --noinput --username admin --email admin@admin.com