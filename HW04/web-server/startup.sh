#!/bin/bash

# check if the directory exists and remove it if it does
if [ -d "/home/ptrandev/ds561-ptrandev-hw04" ]; then
    rm -rf /home/ptrandev/ds561-ptrandev-hw04
fi

# download all files from ds561-ptrandev-hw04 bucket
gsutil -m cp -r gs://ds561-ptrandev-hw04/ /home/ptrandev/

# go to the directory where the flask app is located
cd /home/ptrandev/ds561-ptrandev-hw04

# install dependencies from requirements.txt
apt install python3-pip -y
pip3 install -r requirements.txt

# run the flask app
python3 main.py