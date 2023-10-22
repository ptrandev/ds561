from google.cloud import storage
from google.cloud import pubsub_v1
from google.cloud import logging
from flask import Flask, request
from waitress import serve
import sqlalchemy
from google.cloud.sql.connector import Connector
from dotenv import load_dotenv
import os
import datetime

connector = Connector()

load_dotenv()

INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")


def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )
    return conn


pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

app = Flask(__name__)

HTTP_METHODS = [
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
]

# set up pub sub
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("ds561-trial-project", "banned-countries-topic")

# set up logging; log into web-server-hw04
client = logging.Client()
logging_client = client.logger("web-server-hw04")


def publish_to_database(
    country, is_banned, client_ip, gender, age, income, requested_file, status_code
):
    # insert into database
    with pool.connect() as conn:
        conn.execute(
            sqlalchemy.text(
              """
              INSERT INTO request (time_of_request, requested_file, is_banned, country, client_ip, gender, age, income)
              VALUES (:time_of_request, :requested_file, :is_banned, :country, :client_ip, :gender, :age, :income)
              """
            ),
            dict(
                time_of_request=datetime.datetime.now(),
                requested_file=requested_file,
                is_banned=is_banned,
                country=country,
                client_ip=client_ip,
                gender=gender,
                age=age,
                income=income,
            ),
        )

        # if status_code is not 200, log to fail_request table
        if status_code != 200:
            # get the row we just inserted
            row = conn.execute(sqlalchemy.text("SELECT * FROM request WHERE request_id = LAST_INSERT_ID()")).fetchone()

            # insert into fail_request table
            conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO fail_request (request_id, status_code)
                    VALUES (:request_id, :status_code)
                    """
                ),
                dict(
                    request_id=row[0],
                    status_code=status_code,
                ),
            )

        # commit changes and close connection
        conn.commit()
        conn.close()


@app.route("/", defaults={"path": ""}, methods=HTTP_METHODS)
@app.route("/<path:path>", methods=HTTP_METHODS)
def get_file(path):
    # get information from headers
    country = request.headers.get("X-country")
    client_ip = request.headers.get("X-client-IP")
    gender = request.headers.get("X-gender")
    age = request.headers.get("X-age")
    income = request.headers.get("X-income")

    # get dirname/filename.html from path
    # path should be bucket_name/dirname/filename.html
    bucket_name = path.split("/")[0]
    file_name = "/".join(path.split("/")[1:])

    # publish to banned-countries topic if country is banned
    # (North Korea, Iran, Cuba, Myanmar, Iraq, Libya, Sudan, Zimbabwe and Syria)
    banned_countries = [
        "north korea",
        "iran",
        "cuba",
        "myanmar",
        "iraq",
        "libya",
        "sudan",
        "zimbabwe",
        "syria",
    ]

    # if the country is banned, publish to banned-countries topic
    if country and country.lower() in banned_countries:
        publisher.publish(topic_path, country.encode("utf-8"))
        logging_client.log_text(f"Banned country: {country}")
        publish_to_database(country, True, client_ip, gender, age, income, file_name, 400)
        return "Banned country", 400

    # only accept GET method
    if request.method != "GET":
        logging_client.log_text(f"Method not implemented: {request.method}")
        publish_to_database(country, False, client_ip, gender, age, income, file_name, 501)
        return "Method not implemented", 501

    if file_name is None:
        print("file_name is required")
        publish_to_database(country, False, client_ip, gender, age, income, file_name, 400)
        return "file_name is required", 400

    if bucket_name is None:
        print("bucket_name is required")
        publish_to_database(country, False, client_ip, gender, age, income, file_name, 400)
        return "bucket_name is required", 400

    # get file from bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    if blob.exists():
        blob_content = blob.download_as_string()
        publish_to_database(country, False, client_ip, gender, age, income, file_name, 200)
        return blob_content, 200, {"Content-Type": "text/html; charset=utf-8"}

    logging_client.log_text(f"File not found: {bucket_name}/{file_name}")
    publish_to_database(country, False, client_ip, gender, age, income, file_name, 404)
    return "File not found", 404


serve(app, host="0.0.0.0", port=5000)
