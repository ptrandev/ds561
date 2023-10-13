# Imports the Google Cloud client library
from google.cloud import logging

# Instantiates a client
logging_client = logging.Client()

# The name of the log to write to
log_name = "my-log"
# Selects the log to write to
logger = logging_client.logger(log_name)

# The data to log
text = "Hello, world!"

# Writes the log entry
logger.log_text(text)

print("Logged: {}".format(text))