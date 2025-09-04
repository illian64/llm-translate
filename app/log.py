import logging
import traceback


def logger():
    return logging.getLogger('uvicorn')


def log_exception(message: str, e: Exception) -> None:
    traceback.print_tb(e.__traceback__, limit=10)
    logging.error(message, str(e))