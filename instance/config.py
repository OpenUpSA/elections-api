import logging

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "iec_api_logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/tmp.db'