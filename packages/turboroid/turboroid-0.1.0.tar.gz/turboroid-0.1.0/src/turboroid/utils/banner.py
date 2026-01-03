import importlib.resources as pkg_resources
from turboroid import __version__


from turboroid.logger import logger


def print_banner(filename: str = "banner.txt"):
    """
    Reads and prints a banner file from the current working directory.
    """
    RESOURCE_PACKAGE = "turboroid.resources"

    try:
        banner_content = pkg_resources.read_text(RESOURCE_PACKAGE, filename)

        title = f":: Turboroid :: (v{__version__})"
        separator = "-" * 40

        logger.info("\n%s\n%s\n%s\n%s", separator, banner_content, title, separator)

    except FileNotFoundError:
        pass
    except Exception:
        logger.exception("Warning: Could not read startup banner:", exc_info=True)
