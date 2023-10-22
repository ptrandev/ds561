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


def publish_request_to_database(
    time_of_request, country, is_banned, client_ip, gender, age, income, requested_file
):
    with pool.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO request (time_of_request, requested_file, is_banned, country, client_ip, gender, age, income)
                VALUES (:time_of_request, :requested_file, :is_banned, :country, :client_ip, :gender, :age, :income)
                """
            ),
            dict(
                time_of_request=time_of_request,
                requested_file=requested_file,
                is_banned=is_banned,
                country=country,
                client_ip=client_ip,
                gender=gender,
                age=age,
                income=income,
            )
        )

        conn.commit()
        conn.close()

def publish_fail_request_to_database(
        time_of_request, requested_file, error_code
):
    with pool.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO fail_request (time_of_request, requested_file, error_code)
                VALUES (:time_of_request, :requested_file, :error_code)
                """
            ),
            dict(
                time_of_request=time_of_request,
                requested_file=requested_file,
                error_code=error_code,
            )
        )

        conn.commit()
        conn.close()

@app.route("/", defaults={"path": ""}, methods=HTTP_METHODS)
@app.route("/<path:path>", methods=HTTP_METHODS)
def get_file(path):
    time_of_request = datetime.datetime.now()

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

    is_banned = country.lower() in banned_countries if country else None

    publish_request_to_database(
        time_of_request,
        country,
        is_banned,
        client_ip,
        gender,
        age,
        income,
        file_name,
    )

    # if the country is banned, publish to banned-countries topic
    if is_banned:
        publisher.publish(topic_path, country.encode("utf-8"))
        logging_client.log_text(f"Banned country: {country}")
        publish_fail_request_to_database(
            time_of_request,
            file_name,
            403,
        )
        return "Banned country", 403

    # only accept GET method
    if request.method != "GET":
        logging_client.log_text(f"Method not implemented: {request.method}")
        publish_fail_request_to_database(
            time_of_request,
            file_name,
            501,
        )
        return "Method not implemented", 501

    if file_name is None:
        return "file_name is required", 400

    if bucket_name is None:
        print("bucket_name is required")
        return "bucket_name is required", 400

    # get file from bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    if blob.exists():
        blob_content = blob.download_as_string()
        return blob_content, 200, {"Content-Type": "text/html; charset=utf-8"}

    logging_client.log_text(f"File not found: {bucket_name}/{file_name}")
    publish_fail_request_to_database(
        time_of_request,
        file_name,
        404,
    )
    return "File not found", 404


serve(app, host="0.0.0.0", port=5000)
