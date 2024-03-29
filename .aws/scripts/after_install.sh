#!/bin/bash
chown ec2-user:ec2-user -R /home/ec2-user/honstats
cd /home/ec2-user/honstats
rm -rf venv
virtualenv -p /usr/bin/python3.8 venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate --noinput
./venv/bin/python manage.py collectstatic --noinput
cd ..
cp .env honstats/honstats/.env
service supervisord restart