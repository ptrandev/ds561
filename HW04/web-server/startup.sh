#!/bin/bash

# download all files from ds561-ptrandev-hw04 bucket only if they don't exist yet
gsutil -m cp -r gs://ds561-ptrandev-hw04/ /home/ptrandev/

# go to the directory where the flask app is located
cd /home/ptrandev/ds561-ptrandev-hw04

# install dependencies from requirements.txt
apt install python3-pip -y
pip3 install -r requirements.txt

# run the flask app
python3 -m flask --app main run --host=0.0.0.0