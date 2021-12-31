from hirvikuraattori import mail, settings
from hirvikuraattori.logs import logger


def main():
    try:
        logger.info(f"** Hirvikuraattori {settings.VERSION} starting a run.")
        mail.read_email()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
