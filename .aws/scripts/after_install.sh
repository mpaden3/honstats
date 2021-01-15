#!/bin/bash
chown ec2-user:ec2-user -R /home/ec2-user/honstats
cd /home/ec2-user/honstats
rm -rf venv
virtualenv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python ./manage.py migrate
./venv/bin/python ./manage.py collectstatic
cd ..
cp .env honstats/honstats/.env