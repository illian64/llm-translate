import logging


def logger():
    return logging.getLogger('uvicorn')


def log_exception(message: str, e: Exception) -> None:
    logger().exception(message + ": " + str(e))
