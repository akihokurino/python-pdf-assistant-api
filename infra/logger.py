import logging


def log_info(message: str) -> None:
    """ログ情報を出力する"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.info(message)
