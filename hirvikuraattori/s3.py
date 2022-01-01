import datetime
import json
import time
from os import listdir, getcwd
from os.path import isfile, join, splitext, getsize, getctime
from typing import List, Dict, Tuple

import boto3
from botocore.exceptions import ClientError

from hirvikuraattori import settings
from hirvikuraattori.logs import logger
from hirvikuraattori.utils import humanize_file_size


def load_tracker_json() -> List[Dict]:
    try:
        with open(settings.S3_TRACKER_JSON_FILE, encoding="utf-8") as tracker_file:
            processed_mails = json.load(tracker_file)
            return processed_mails
    except FileNotFoundError:
        return []
    except json.decoder.JSONDecodeError:
        logger.exception("The S3 tracker JSON file was corrupt. Reprocessing all downloaded photos.")
        return []


def write_tracker_json(previously_processed_photos: List[Dict], new_processed_photos: List[Dict]) -> None:
    processed_photos = previously_processed_photos + new_processed_photos
    processed_photos.sort(key=lambda x: x["filename"])

    with open(settings.S3_TRACKER_JSON_FILE, "w", encoding="utf-8") as tracker_file:
        json.dump(processed_photos, tracker_file, ensure_ascii=False, indent=2)


def filter_photos_from_files(filenames: List[str]) -> List[str]:
    photo_filenames = set()
    for filename in filenames:
        _, extension = splitext(filename)
        if extension.lower()[1:] in settings.SUPPORTED_IMAGE_EXTENSIONS:
            photo_filenames.add(filename)

    return photo_filenames


def get_unprocessed_photos() -> Tuple[List[str], List[Dict]]:
    processed_filenames, previously_processed_photos = get_processed_photos()
    working_directory = getcwd()
    all_filenames = set([f for f in listdir(working_directory) if isfile(join(working_directory, f))])
    photo_filenames = filter_photos_from_files(all_filenames)
    unprocessed_filenames = photo_filenames - processed_filenames
    logger.info(f"Found {len(unprocessed_filenames)} new photos to upload.")
    return unprocessed_filenames, previously_processed_photos


def get_processed_photos() -> Tuple[List[str], List[Dict]]:
    try:
        previously_processed_photos = load_tracker_json()
        processed_filenames = set([f"{photo['filename']}" for photo in previously_processed_photos])
        return processed_filenames, previously_processed_photos
    except IOError:
        return set(), []


def upload_file(filename):
    s3_client = boto3.client(
        service_name='s3',
        aws_access_key_id=settings.S3_USER_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_USER_SECRET_ACCESS_KEY,
    )
    s3_object_name = filename
    logger.debug("Uploading file '{s3_object_name}'.")
    s3_client.upload_file(filename, settings.S3_BUCKET_NAME, s3_object_name)


def process_photo(filename: str) -> Dict:
    upload_file(filename)
    photo = {
        "filename": filename,
        "size": humanize_file_size(getsize(filename)),
        "created": getctime(filename),
        "processed": f"{datetime.datetime.now()}",
    }
    return photo


def process_photos(filenames_to_process: List[str]) -> List[Dict]:
    processed_photos = []
    for filename in filenames_to_process:
        time.sleep(settings.SLEEP_TIME_SECONDS_BETWEEN_UPLOADS)
        try:
            photo = process_photo(filename)
            processed_photos.append(photo)
        except OSError:
            logger.exception(f"Error accessing the file '{filename}' before upload.")
        except ClientError as e:
            logger.exception(f"S3 client error while uploading the file '{filename}': {e}.")

    return processed_photos


def push_photos() -> None:
    logger.info(f"Pushing new photos to S3 bucket: {settings.S3_BUCKET_NAME}")
    filenames_to_process, previously_processed_photos = get_unprocessed_photos()
    new_processed_photos = process_photos(filenames_to_process)
    if new_processed_photos:
        write_tracker_json(previously_processed_photos, new_processed_photos)