import logging
import secrets

LOG_LEVEL = logging.DEBUG


def log_setup():
    """
    Sets the log level.
    No easy way other than to override AWS Lambda default handlers.
    """
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='YYYYY %(asctime)s %(message)s', level=LOG_LEVEL)



