#!/bin/bash
chown ec2-user:ec2-user -R /home/ec2-user/honstats
cd /home/ec2-user/honstats
rm -rf venv
virtualenv venv
source install_virtualenv.sh