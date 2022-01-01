import logging
from logging.handlers import RotatingFileHandler

from hirvikuraattori import settings


logFormatter = logging.Formatter("%(asctime)s %(levelname)-3.3s %(message)s")
logger = logging.getLogger()

fileHandler = RotatingFileHandler(
    settings.LOG_FILE,
    maxBytes=512*1024,
    backupCount=7,
)
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(settings.LOG_LEVEL)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(settings.LOG_LEVEL)
logger.addHandler(consoleHandler)

logger.setLevel(settings.LOG_LEVEL)
