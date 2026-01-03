import logging
import sys

logger = logging.getLogger("turboroid")
logger.addHandler(logging.NullHandler())


def setup_turboroid_logging(level=logging.INFO):
    logger.setLevel(level)
    if not logger.handlers or isinstance(logger.handlers[0], logging.NullHandler):
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "\033[32m%(asctime)s\033[0m [%(levelname)s] \033[34m%(name)s\033[0m: %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
