# DS561 HW05

For your convenience, the code relevant for each VM has been separated into its own folder.

## web-server

This code is used for the web-server-hw04 VM.

- `main.py` - The Flask web server using waitress as the WSGI server.
- `requirements.txt` - The Python requirements for the web server.

## http-client

This code is used for the http-client-hw04 VM.

- `http-client.py` - The http client provided by the professor. This allows us to send requests to the web server.
- `http-client-multiple-instances.sh` - This allows us to spin up multiple `http-client.py` instances at once. You can use a simple argument to specify the number of instances to spin up. For example, `./http-client-multiple-instances.sh 2` will spin up 2 instances of `http-client.py` at once. This script uses the random seed `1337` and will send 50,000 requests per instance to the web server. This allows us to get a deterministic sample for testing purposes.