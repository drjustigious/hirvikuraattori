import os
from dotenv import load_dotenv
from pathlib import Path

VERSION = "0.0.1"


# Load settings from environment variables.
dotenv_directory = Path(os.path.dirname(__file__)).parent.absolute()
dotenv_path = os.path.join(dotenv_directory, ".env")
load_dotenv(dotenv_path)

MAILBOX_ADDRESS = os.getenv("MAILBOX_ADDRESS")
MAILBOX_PASSWORD = os.getenv("MAILBOX_PASSWORD")

IMAP_SERVER_ADDRESS = os.getenv("IMAP_SERVER_ADDRESS")
IMAP_SERVER_PORT = os.getenv("IMAP_SERVER_PORT")

MAIL_TRACKER_JSON_FILE = os.getenv("MAIL_TRACKER_JSON_FILE")
S3_TRACKER_JSON_FILE = os.getenv("S3_TRACKER_JSON_FILE")
LOG_FILE = os.getenv("LOG_FILE")
LOG_LEVEL = os.getenv("LOG_LEVEL")

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_USER_ACCESS_KEY_ID = os.getenv("S3_USER_ACCESS_KEY_ID")
S3_USER_SECRET_ACCESS_KEY = os.getenv("S3_USER_SECRET_ACCESS_KEY")


### Additional settings. ###

# Only these file types are downloaded and uploaded.
SUPPORTED_IMAGE_EXTENSIONS = [
    "jpg", "jpeg", "png"
]

# The metadata fields stored in the email processing tracker JSON file.
STORED_EMAIL_METADATA = [
    "subject", "from", "date"
]

SLEEP_TIME_SECONDS_BETWEEN_EMAILS = 0.2
SLEEP_TIME_SECONDS_BETWEEN_UPLOADS = 0.2