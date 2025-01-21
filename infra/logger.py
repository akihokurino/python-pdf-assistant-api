import logging

from adapter.adapter import LogAdapter


class LoggerImpl(LogAdapter):
    def __init__(
            self,
    ) -> None:
        pass

    @classmethod
    def new(
            cls,
    ) -> LogAdapter:
        return cls()

    def log_info(self, message: str) -> None:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger()
        logger.info(message)

    def log_error(self, e: Exception) -> None:
        logging.basicConfig(level=logging.ERROR)
        logger = logging.getLogger()
        logger.info("An error occurred", exc_info=e)
