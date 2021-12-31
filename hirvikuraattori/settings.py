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
LOG_FILE = os.getenv("LOG_FILE")
LOG_LEVEL = os.getenv("LOG_LEVEL")
