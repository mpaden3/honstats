cd /home/ec2-user/honstats
source venv/bin/activate
pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic
cd ..
cp .env honstats/honstats/.env