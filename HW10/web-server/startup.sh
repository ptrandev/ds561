#!/bin/bash

# check if the directory exists; if not, copy the files from the bucket to the directory
if [ -d "/root/ds561-ptrandev-hw05" ]; then
    echo "Directory /root/ds561-ptrandev-hw05 exists."
else
    # copy the files from the bucket to the directory
    gsutil -m cp -r gs://ds561-ptrandev-hw05/ /root/
fi

# go to the directory where the flask app is located
cd /root/ds561-ptrandev-hw05

# install dependencies from requirements.txt
apt install python3-pip -y
pip3 install -r requirements.txt

# run the flask app
python3 main.py