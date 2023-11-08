# DS561 HW06

There are two files used for exploration of the data and figuring out which model to select for the final Python program:
1. `download_data.py` - downloads the data from the database and saves it to a CSV file. This data is used in the Python notebook to explore the data and test different models.
2. `models.ipynb` - a Python notebook that explores the data and tests different models. This serves as a testing bed for the final Python program.

The final Python program is `predict.py`. This program is capable of fetching the data from the database and training the models to perform predictions.

## Usage

`download_data.py` and `predict.py` use the same options to connect to the database:
- `--instance_connection_name` - The connection name of the Cloud SQL instance (default: ds561-trial-project:us-east4:ds561-ptrandev-hw05)
- `--db_user` - The username to use to connect to the database (default: root)
- `--db_password` - The password to use to connect to the database. This is a required option and has no default value.
- `--db_name` - The name of the database to connect to (default: ds561-ptrandev-hw05)

Example:

```
$ python3 download_data.py --db_password=PASSWORD --db_name=ds561-ptrandev-hw05 --instance_connection_name=ds561-trial-project:us-east4:ds561-ptrandev-hw05 --db_user=root

Downloading data from database...

Training Random Forest Classifier...
Accuracy of predicting country with client ip:  1.0

Training Random Forest Classifier...
Accuracy of predicting income:  0.82755
```