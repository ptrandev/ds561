# DS561 HW09

For your convenience, the code relevant for each server has been separated into its own folder.

## web-server

This code is used for the web-server-hw09 docker container, which will be deployed to GKE.

- `main.py` - The Flask web server using waitress as the WSGI server.
- `requirements.txt` - The Python requirements for the web server.
- `Dockerfile` - The Dockerfile used to build the Docker image for the web server.
- `compose.yaml` - The docker-compose file used to run the web server.
- `.dockerignore` - The .dockerignore file used to ignore files when building the Docker image.
- `web-server-hw09.yaml` - The kubernetes deployment file for the web server.

## http-client

This code is used for the http-client-hw04 VM.

- `http-client.py` - The http client provided by the professor. This allows us to send requests to the web server.

## forbidden-requests

This code is used for the forbidden-requests-hw04 VM.

- `forbidden-requests.py` - This is a simple Python script that listens for pub/sub messages published by the web server. It will print to the console when it receives a message.
- `requirements.txt` - The Python requirements for the forbidden-requests script.