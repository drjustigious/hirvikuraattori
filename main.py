import datetime

from hirvikuraattori import mail, settings, s3
from hirvikuraattori.logs import logger


def main():
    try:
        logger.warning(f"Hirvikuraattori {settings.VERSION} starting a run.")
        start_time = datetime.datetime.now()

        mail.read_inbox()
        download_complete_time = datetime.datetime.now()
        download_seconds = round(
            (download_complete_time-start_time).total_seconds())
        logger.info(
            f"Photos downloaded from email in {(download_seconds)} seconds.")

        s3.push_photos()
        upload_complete_time = datetime.datetime.now()
        upload_seconds = round(
            (upload_complete_time-download_complete_time).total_seconds())
        logger.info(
            f"Photos uploaded to S3 bucket in {(upload_seconds)} seconds.")

        total_runtime = round(
            (upload_complete_time - start_time).total_seconds())
        logger.warning(f"Run completed in {(total_runtime)} seconds.")
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
