# DS561 HW04

For your convenience, the code relevant for each VM has been separated into its own folder.

## web-server

This code is used for the web-server-hw04 VM.

- `main.py` - The Flask web server using waitress as the WSGI server. This has been uploaded to gs://ds561-ptrandev-hw04/main.py for the startup script to download.
- `requirements.txt` - The Python requirements for the web server. This has been uploaded to gs://ds561-ptrandev-hw04/requirements.txt for the startup script to download.
- `startup.sh` - This will be pasted into the Automation > Startup script section when we are creating the VM. This will download the `main.py` and `requirements.txt` files from the bucket, install the requirements, and start the web server.

## http-client

This code is used for the http-client-hw04 VM.

- `http-client.py` - The http client provided by the professor. This allows us to send requests to the web server.
- `http-client-multiple-instances.sh` - This allows us to spin up multiple `http-client.py` instances at once to stress test the web server. You can use a simple argument to specify the number of instances to spin up. For example, `./http-client-multiple-instances.sh 10` will spin up 10 instances of `http-client.py` at once.

## forbidden-requests

This code is used for the forbidden-requests-hw04 VM.

- `forbidden-requests.py` - This is a simple Python script that listens for pub/sub messages published by the web server. It will print to the console when it receives a message.
- `requirements.txt` - The Python requirements for the forbidden-requests script.