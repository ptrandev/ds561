# DS561 HW03

- `http-client.py` is the client program provided by Professor.
- `cloud-function` contains the cloud function code.
- `forbidden-requests` contains the client program that listens to published events from Pub/Sub published by the cloud function.

## Cloud Function

Setting up the cloud function for local testing and deployment:

```
$ cd HW03/cloud-function
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Running locally:

```
$ functions-framework --target=get_file
```

Deploying the cloud function:

```
$ gcloud functions deploy ds561-ptrandev-hw03 --gen2 --runtime=python311 --region=us-east4 --source=. --entry-point=get_file --trigger-http --allow-unauthenticated --max-instances=20
```

## Forbidden Requests

Set up a python virtual environment and install dependencies for `forbidden-requests.py`:

```
$ cd HW03/forbidden-requests
$ python3 -m venv env
$ source /env/bin/activate
$ pip install -r requirements.txt
```

We can run the `forbidden-requests.py` script to listen to forbidden requests. Here is an example of the output when a request from a banned country is made:

```
$ python3 forbidden-requests.py
Listening for banned countries...
Received message: Message {
  data: b'Iran'
  ordering_key: ''
  attributes: {}
}
```

A forbidden request looks like this to http-client.py:

```
$ python3 http-client.py --domain=ds561-ptrandev-hw03-2ry3l7rzva-uk.a.run.app --bucket=/ds561-ptrandev-hw02 --webdir=html --verbose --num_requests=1 --index=1 --ssl
/Users/phillip/Git/ds561-hw02/HW03/http-client.py:65: DeprecationWarning: ssl.PROTOCOL_TLS is deprecated
  ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
Requesting  /ds561-ptrandev-hw02/html/0.html  from  ds561-ptrandev-hw03-2ry3l7rzva-uk.a.run.app 443
400 Bad Request
content-type: text/html; charset=utf-8
X-Cloud-Trace-Context: 5c976e900ecd8a36f3b267eda995b6c6;o=1
Date: Tue, 10 Oct 2023 17:21:17 GMT
Server: Google Frontend
Content-Length: 14
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000


b'Banned country'
```

## HTTP Client

First, we get the cloud function URL needed to call the function:

```
$ gcloud functions describe ds561-ptrandev-hw03 --gen2 --region us-east4 --format='value(serviceConfig.uri)'
https://ds561-ptrandev-hw03-2ry3l7rzva-uk.a.run.ap
```

Now we can test with a single request:

```
$ python3 http-client.py --domain=ds561-ptrandev-hw03-2ry3l7rzva-uk.a.run.app --bucket=/ds561-ptrandev-hw02 --webdir=html --verbose --num_requests=1 --index=1 --ssl
/Users/phillip/Git/ds561-hw03/http-client.py:63: DeprecationWarning: ssl.PROTOCOL_TLS is deprecated
  ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
Requesting  /ds561-ptrandev-hw02/html/0.html  from  ds561-ptrandev-hw03-2ry3l7rzva-uk.a.run.app 443
200 OK
content-type: text/html; charset=utf-8
X-Cloud-Trace-Context: dbd5369b96f3d2f3902c760236a5a835;o=1
Date: Sun, 08 Oct 2023 17:22:33 GMT
Server: Google Frontend
Content-Length: 106949
Alt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000


b'<!DOCTYPE html>\n<html>\n<body>\nLorem ipsum dolor sit amet, ...
```

Or with a few hundred:

```
$ python3 http-client.py --domain=ds561-ptrandev-hw03-2ry3l7rzva-uk.a.run.app --bucket=/ds561-ptrandev-hw02 --webdir=html --num_requests=200 --index=20000 --ssl --verbose
```