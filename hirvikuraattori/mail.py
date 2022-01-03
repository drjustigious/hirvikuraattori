import datetime
import email
from email.header import decode_header
from email.message import Message
import imaplib
import json
import os
import time
from typing import List, Dict, Set, ByteString, Tuple

from hirvikuraattori import settings
from hirvikuraattori.logs import logger


def load_tracker_json() -> List[Dict]:
    try:
        with open(settings.MAIL_TRACKER_JSON_FILE, encoding="utf-8") as tracker_file:
            processed_mails = json.load(tracker_file)
            return processed_mails
    except FileNotFoundError:
        return []
    except json.decoder.JSONDecodeError:
        logger.exception(
            "The email tracker JSON file was corrupt. Reprocessing the whole inbox.")
        return []


def write_tracker_json(previously_processed_emails: List[Dict], new_processed_emails: List[Dict]) -> None:
    processed_emails = previously_processed_emails + new_processed_emails
    processed_emails.sort(key=lambda x: x["id"])

    with open(settings.MAIL_TRACKER_JSON_FILE, "w", encoding="utf-8") as tracker_file:
        json.dump(processed_emails, tracker_file, ensure_ascii=False, indent=2)


def get_processed_email_ids() -> Tuple[Set[str], List[Dict]]:
    try:
        previously_processed_emails = load_tracker_json()
        processed_ids = set(
            [f"{message['id']}" for message in previously_processed_emails])
        return processed_ids, previously_processed_emails
    except IOError:
        return set(), []


def get_unprocessed_email_ids(data: ByteString) -> Set[str]:
    all_ids = split_data_to_ids(data)
    processed_ids, previously_processed_emails = get_processed_email_ids()
    unprocessed_ids = all_ids - processed_ids
    logger.info(f"Found {len(unprocessed_ids)} new email messages to process.")
    return unprocessed_ids, previously_processed_emails


def split_data_to_ids(data: ByteString) -> Set[str]:
    ids = set()
    for id_string in data.decode("utf-8").split(" "):
        try:
            ids.add(f"{int(id_string)}")
        except ValueError:
            pass

    return ids


def get_email_message(email_data: ByteString) -> Message:
    email_message = email.message_from_bytes(
        email_data[0][1]
    )
    return email_message


def get_email_message_dict(email_message: Message, email_id: str):
    message_dict = {"id": int(email_id)}

    for key in settings.STORED_EMAIL_METADATA:
        data, encoding = decode_header(email_message.get(key, ''))[0]
        if encoding:
            value = data.decode(encoding)
        else:
            value = data
        message_dict[key] = value

    return message_dict


def attachment_is_downloadable(part: Message) -> bool:
    attachment_filename = part.get_filename()
    _, extension = os.path.splitext(attachment_filename)

    if extension.lower()[1:] not in settings.SUPPORTED_IMAGE_EXTENSIONS:
        supported_extensions = ", ".join(settings.SUPPORTED_IMAGE_EXTENSIONS)
        logger.debug(
            f"Skipping email attachment '{attachment_filename}' because it is not one of the supported types ({supported_extensions}).")
        return False

    return True


def download_attachment(part: Message, message_dict: Dict) -> None:
    attachment_filename = part.get_filename()
    with open(attachment_filename, "wb") as downloaded_file:
        downloaded_file.write(part.get_payload(decode=True))
    logger.info(
        f"Email from {message_dict['from']} {message_dict['date']} '{message_dict['subject']}': Downloaded attachment '{attachment_filename}'.")
    if "downloads" not in message_dict:
        message_dict["downloads"] = []
    message_dict["downloads"].append(attachment_filename)


def process_email(mail: imaplib.IMAP4_SSL, email_id: str) -> Dict:
    # Reference: https://medium.com/@sdoshi579/to-read-emails-and-download-attachments-in-python-6d7d6b60269

    response, data = mail.fetch(email_id, "(RFC822)")
    assert response == "OK"

    email_message = get_email_message(data)
    message_dict = get_email_message_dict(email_message, email_id)
    for part in email_message.walk():
        skip_this_part = (
            part.get_content_maintype() == "multipart" or
            part.get('Content-Disposition') is None or
            not part.get_filename()
        )
        if skip_this_part:
            continue
        if not attachment_is_downloadable(part):
            continue
        download_attachment(part, message_dict)

    message_dict["processed"] = f"{datetime.datetime.now()}"
    return message_dict


def process_emails(mail: imaplib.IMAP4_SSL, email_ids: str) -> List[Dict]:
    new_processed_emails = []
    for email_id in email_ids:
        time.sleep(settings.SLEEP_TIME_SECONDS_BETWEEN_EMAILS)
        new_processed_emails.append(process_email(mail, email_id))
    return new_processed_emails


def read_inbox() -> None:
    logger.info(f"Reading mailbox: {settings.MAILBOX_ADDRESS}")

    mail = imaplib.IMAP4_SSL(settings.IMAP_SERVER_ADDRESS)
    mail.login(settings.MAILBOX_ADDRESS, settings.MAILBOX_PASSWORD)
    mail.select("inbox")

    response, data = mail.search(None, "ALL")
    assert response == "OK"
    if not data:
        return

    email_ids, previously_processed_emails = get_unprocessed_email_ids(data[0])
    new_processed_emails = process_emails(mail, email_ids)

    if new_processed_emails:
        write_tracker_json(previously_processed_emails, new_processed_emails)
