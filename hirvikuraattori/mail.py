import imaplib
import json
from typing import List, Dict

from hirvikuraattori import settings
from hirvikuraattori.logs import logger


def get_processed_mails() -> List[Dict]:
    try:
        with open(settings.MAIL_TRACKER_JSON_FILE) as tracker_file:
            processed_mails = json.load(tracker_file)
            return processed_mails
    except IOError:
        return []


def read_email() -> None:
    logger.info(f"Reading mailbox: {settings.MAILBOX_ADDRESS}")

    mail = imaplib.IMAP4_SSL(settings.IMAP_SERVER_ADDRESS)
    mail.login(settings.MAILBOX_ADDRESS, settings.MAILBOX_PASSWORD)
    mail.select("inbox")

    status, mail_ids = mail.search(None, "ALL")
    assert status == "OK"
    print(mail_ids)
