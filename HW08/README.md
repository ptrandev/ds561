# DS561 HW08

## web-server

This code is used for the web-server-01-hw08 and web-server-02-hw08 VMs.

- `main.py` - The Flask web server using waitress as the WSGI server. This has been uploaded to gs://ds561-ptrandev-hw08/main.py for the startup script to download.
- `requirements.txt` - The Python requirements for the web server. This has been uploaded to gs://ds561-ptrandev-hw08/requirements.txt for the startup script to download.
- `startup.sh` - This will be pasted into the Automation > Startup script section when we are creating the VM. This will download the `main.py` and `requirements.txt` files from the bucket, install the requirements, and start the web server.

## http-client

This code has been modified to print out the X-GCP-ZONE header when it is run in `--verbose` mode. Additionally, the client now implements a 5 second timeout when connecting to the server. When a response is not received within 5 seconds, the client will print out a timeout message. This allows us to test our load balancer's health check.