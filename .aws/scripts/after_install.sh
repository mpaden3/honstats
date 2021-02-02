#!/bin/bash
chown ec2-user:ec2-user -R /home/ec2-user/honstats
cd /home/ec2-user/honstats
rm -rf venv
/usr/bin/python3 -m virtualenv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate -no-input
./venv/bin/python manage.py collectstatic -no-input
cd ..
cp .env honstats/honstats/.env
service supervisord restart