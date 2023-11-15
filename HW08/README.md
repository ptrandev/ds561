# DS561 HW08

## web-server

This code is used for the web-server-01-hw08 and web-server-02-hw08 VMs.

- `main.py` - The Flask web server using waitress as the WSGI server. This has been uploaded to gs://ds561-ptrandev-hw08/main.py for the startup script to download.
- `requirements.txt` - The Python requirements for the web server. This has been uploaded to gs://ds561-ptrandev-hw08/requirements.txt for the startup script to download.
- `startup.sh` - This will be pasted into the Automation > Startup script section when we are creating the VM. This will download the `main.py` and `requirements.txt` files from the bucket, install the requirements, and start the web server.

It is important to modify the `export GCP_ZONE=` line in the `startup.sh` script to match the zone that the VM is in. This is used to set the `X-GCP-ZONE` header.

## http-client

This code has been modified to print out the X-GCP-ZONE header and the timestamp of when the request has been fulfilled when it is run in `--verbose` mode.

Additionally, the client now implements a 5 second timeout when connecting to the server. When a response is not received within 5 seconds, the client will print out a timeout message. This allows us to test our load balancer's health check.

Here is an example of the client running in verbose mode:

```
$ python3 http-client.py --domain=35.245.242.165 --bucket=/ds561-ptrandev-hw02 --webdir=html --verbose --num_requests=10000 --index=1000 --port=5000
Requesting  /ds561-ptrandev-hw02/html/672.html  from  35.245.242.165 5000
00:40:26 200 OK us-east4-a
Requesting  /ds561-ptrandev-hw02/html/598.html  from  35.245.242.165 5000
00:40:26 200 OK us-east4-b
Requesting  /ds561-ptrandev-hw02/html/187.html  from  35.245.242.165 5000
00:40:26 200 OK us-east4-a
...
```