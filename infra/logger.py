import logging


def log_info(message: str) -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.info(message)


def log_error(e: Exception) -> None:
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger()
    logger.info("An error occurred", exc_info=e)
