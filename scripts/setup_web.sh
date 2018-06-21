#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-dev nginx
sudo pip3 install virtualenv
mkdir ~/myproject
cd ~/myproject
virtualenv myprojectenv
source myprojectenv/bin/activate
pip install gunicorn flask tensorflow keras Pillow boto3 redis
git clone https://github.com/takenoko-str/sqs-batch-server.git
cd sqs-batch-server/

cd /var/www/html

ln -s /home/ubuntu/myproject/sqs-batch-server sqs-batch-server

