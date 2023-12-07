# DS561 HW10

For your convenience, the code relevant for each portion has been separated into its own folder.

## web-server

This code is used for the web-server-hw10 VM.

- `main.py` - The Flask web server using waitress as the WSGI server.
- `requirements.txt` - The Python requirements for the web server.
- `generate-content.py` - The Python script that generates the content for the mini-web. Provided by the professor.

Not provided:

- `.env` - This file contains the credentials necessary for the web server to access the database. You must create this file yourself. Instructions are included in the PDF file. The file should be in the following format:

```
PROJECT_ID=PROJECT_ID_FROM_PDF_FILE
DB_USER=root
DB_NAME=DB_NAME_FROM_PDF_FILE
DB_PASSWORD=PASSWORD_FROM_PDF_FILE
INSTANCE_CONNECTION_NAME=INSTANCE_CONNECTION_NAME_FROM_PDF_FILE
```

## http-client

This code is used to test the web-server-hw10 VM.

- `http-client.py` - The http client provided by the professor. This allows us to send requests to the web server.

## hw10.yaml

This file is used to create the entire deployment on GCP. You can run it with the following command:

```
gcloud deployment-manager deployments create hw10 --config hw10.yaml
```

And to delete the deployment:

```
gcloud deployment-manager deployments delete hw10
```