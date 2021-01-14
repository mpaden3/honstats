cd /home/ec2-user/honstats
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic