# download data from a google SQL database

import sys
import sqlalchemy
import argparse
from google.cloud.sql.connector import Connector
from tqdm import tqdm

connect = Connector()

# download data from database
# there are two tables: request and fail_request
def download_data():
    with pool.connect() as conn:
        # get all data from request table
        request = conn.execute(sqlalchemy.text("SELECT * FROM request"))
        request_data = request.fetchall()

        # get all data from fail_request table
        fail_request = conn.execute(sqlalchemy.text("SELECT * FROM fail_request"))
        fail_request_data = fail_request.fetchall()

        print("Pulled data from database!")

        # write data to csv files
        write_to_csv(request_data, "request.csv")
        write_to_csv(fail_request_data, "fail_request.csv")
        
        print("Wrote data to .csv files!")

        conn.close()

# write data to CSV files
def write_to_csv(data, file_path):
    with open(file_path, "w") as f:
        for row in tqdm(data):
            f.write(",".join([str(x) for x in row]) + "\n")
        f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance_connection_name", help="Cloud SQL Instance Connection Name", default="ds561-trial-project:us-east4:ds561-ptrandev-hw05")
    parser.add_argument("--db_user", help="Database User", default="root")
    parser.add_argument("--db_password", help="Database Password", required=True)
    parser.add_argument("--db_name", help="Database Name", default="ds561-ptrandev-hw05")

    args = parser.parse_args()

    INSTANCE_CONNECTION_NAME = args.instance_connection_name
    DB_USER = args.db_user
    DB_PASSWORD = args.db_password
    DB_NAME = args.db_name

    print("Connecting to database...")

    # connect to database
    def getconn():
        conn = connect.connect(
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

    print("Downloading data from database...")

    download_data()