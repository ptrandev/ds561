import sqlalchemy
import argparse
from google.cloud.sql.connector import Connector
from tqdm import tqdm
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

connect = Connector()

# possible values for age, income, gender from http-client.py
list_of_ages = ["0-16", "17-25", "26-35", "36-45", "46-55", "56-65", "66-75", "76+"]
list_of_incomes = [
    "0-10k",
    "10k-20k",
    "20k-40k",
    "40k-60k",
    "60k-100k",
    "100k-150k",
    "150k-250k",
    "250k+",
]
list_of_genders = ['Male', 'Female']

# download data from database
# there are two tables: request and fail_request
def download_data():
    print("Downloading data from database...")

    with pool.connect() as conn:
        # get all data from request table
        request = conn.execute(sqlalchemy.text("SELECT * FROM request"))
        request_data = request.fetchall()
        conn.close()

    # turn into pandas dataframe
    df = pd.DataFrame(
        request_data,
        columns=[
            "request_id",
            "time_of_request",
            "requested_file",
            "is_banned",
            "country",
            "client_ip",
            "gender",
            "age",
            "income",
        ],
    )

    return df


def predict_country_with_client_ip(df):
    # operate on a copy of the dataframe
    df = df.copy()

    # drop all columns except country and client_ip
    df.drop(df.columns.difference(["country", "client_ip"]), axis=1, inplace=True)

    # split ip into 4 columns
    df[["ip1", "ip2", "ip3", "ip4"]] = df.client_ip.str.split(
        ".",
        expand=True,
    )

    # drop client_ip column
    df.drop(["client_ip"], axis=1, inplace=True)

    # drop ip4 column
    df.drop(["ip4"], axis=1, inplace=True)

    # encode country labels
    encoder = LabelEncoder()

    df["country"] = encoder.fit_transform(df["country"])

    # split into training and testing data
    X_train, y_train, X_test, y_test = create_train_test_split(df, "country")

    # train model
    rf = train_random_forest_classifier(X_train, y_train)

    # make predictions
    accuracy = predict_random_forest_classifier(rf, X_test, y_test)

    print("Accuracy of predicting country with client ip: ", accuracy)


def predict_income(df):
    df = df.copy()

    # drop request_id, time_of_request, is_banned, client_ip
    df.drop(
        ["request_id", "time_of_request", "is_banned", "client_ip"],
        axis=1,
        inplace=True,
    )

    # turn requested_file column from 'html/1.html' to '1'
    df["requested_file"] = (
        df["requested_file"].str.split("/").str[1].str.split(".").str[0]
    )

    # turn into boolean values
    df["gender"] = df["gender"].map(lambda x: list_of_genders.index(x))

    # turn age into integer values using list_of_ages
    df["age"] = df["age"].map(lambda x: list_of_ages.index(x))

    # turn income into integer values using list_of_incomes
    df["income"] = df["income"].map(lambda x: list_of_incomes.index(x))

    # encode country labels
    encoder = LabelEncoder()

    df["country"] = encoder.fit_transform(df["country"])

    # create test and train sets
    X_train, y_train, X_test, y_test = create_train_test_split(df, "income")

    # train model
    rf = train_random_forest_classifier(X_train, y_train)

    # make predictions
    accuracy = predict_random_forest_classifier(rf, X_test, y_test)

    print("Accuracy of predicting income: ", accuracy)

def train_random_forest_classifier(X_train, y_train):
    # train model
    rf = RandomForestClassifier()

    print("Training Random Forest Classifier...")

    rf.fit(X_train, y_train)

    return rf

def predict_random_forest_classifier(rf, X_test, y_test):
    # make predictions
    y_pred = rf.predict(X_test)

    # calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)

    return accuracy

def create_train_test_split(df, column):
    # create test and train sets
    train, test = train_test_split(df, test_size=0.2)

    # split train and test sets into X and y
    X_train = train.drop(column, axis=1)
    y_train = train[column]

    X_test = test.drop(column, axis=1)
    y_test = test[column]

    return X_train, y_train, X_test, y_test

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--instance_connection_name",
        help="Cloud SQL Instance Connection Name",
        default="ds561-trial-project:us-east4:ds561-ptrandev-hw05",
    )
    parser.add_argument("--db_user", help="Database User", default="root")
    parser.add_argument("--db_password", help="Database Password", required=True)
    parser.add_argument(
        "--db_name", help="Database Name", default="ds561-ptrandev-hw05"
    )

    args = parser.parse_args()

    INSTANCE_CONNECTION_NAME = args.instance_connection_name
    DB_USER = args.db_user
    DB_PASSWORD = args.db_password
    DB_NAME = args.db_name

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

    # download data from database
    df = download_data()

    print()

    # run prediction models on data
    predict_country_with_client_ip(df)

    print()

    predict_income(df)
