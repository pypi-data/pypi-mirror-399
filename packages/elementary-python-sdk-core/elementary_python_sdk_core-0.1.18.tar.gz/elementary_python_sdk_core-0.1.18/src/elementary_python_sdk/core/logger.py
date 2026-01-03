import logging

LOGGER_NAME = "elementary-python-sdk"


def get_logger():
    return logging.getLogger(LOGGER_NAME)
