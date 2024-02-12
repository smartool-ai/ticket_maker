import logging
import os
from time import gmtime
from typing import Optional

PACKAGE_NAME = "jkbx"
LOGGING_FORMAT = (
    "[%(asctime)s][%(levelname)s][%(filename)s"
    ":%(lineno)d][%(requestId)s]: %(message)s"
)


def _setup_logger(
    logger: logging.Logger,
    log_level: int,
    file_name: Optional[str] = None,
) -> None:
    """Shared setup for setup and module logger.

    log_level is usually something like logging.DEBUG but these different log levels are
    defined as integers.
    """

    logger.setLevel(log_level)
    formatter = logging.Formatter(LOGGING_FORMAT)
    formatter.converter = gmtime

    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(log_level)
    streamhandler.setFormatter(formatter)
    logger.addHandler(streamhandler)

    if file_name:
        os.makedirs("logs/", exist_ok=True)
        filehandler = logging.FileHandler(f"logs/{file_name}.log")
        filehandler.setLevel(logging.INFO)
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)


def setup_service_logger(
    service_name: str, log_level: int, to_file: bool = False
) -> logging.LoggerAdapter:
    """Set up and return a logger for this service."""
    logger = logging.getLogger(PACKAGE_NAME)
    file_name = service_name if to_file else None
    _setup_logger(logger, log_level, file_name)
    adapter = logging.LoggerAdapter(logger, extra={"requestId": None})
    return adapter


# If we delete all the handlers on the root logger, we can set propagate = True, which means we can
# use caplog in unit tests


def initialize_lambda_logger() -> logging.Logger:
    """Modify the handler(s) on the root logger to use our desired formatter.

    Lambda appears to be doing some trickery behind the scenes in its default handler to convert
    newlines within messages to \r so that CloudWatch groups them together in one log. Replacing
    the handler loses this behavior, so tracebacks then get split across multiple entries.

    propagate = True means that log messages get forwarded up the logging hierarchy
    eventually to the root logger.  caplog subscribes to the root logger, which means that if we
    want to use caplog in unit tests, we have to either subscribe to the root logger or keep
    propagate = True.  However, the root logger by default already has handlers attached,
    so if we attach handlers to our own lambda logger, multiple handlers will pick up the event
    and we will encounter duplicate logs in production.  Deleting the default handlers on the
    root logger allows propagate = True while also having a custom handler on our lambda logger.
    """
    root_logger = logging.getLogger()
    formatter = logging.Formatter(
        "[%(levelname)s]\t" "[%(filename)s:%(lineno)d]\t" "%(message)s\n"
    )
    formatter.converter = gmtime
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
    root_logger.propagate = True
    root_logger.setLevel(logging.INFO)
    return root_logger


lambda_logger = initialize_lambda_logger()


def get_module_logger() -> logging.Logger:
    """Return the single logger usable across all of our lambda functions.

    The root (unnamed) logger already has a streamhandler, but its formatter lacks certain
    details so we name our logger to distinguish it from the root logger and then turn
    propagation off so that the root logger doesn't also receive our log messages.

    The logger is prepared at compile time so that addHandler is only called once - otherwise
    multiple handlers could be attached to the lambda logger.  This allows us to avoid using
    multiple named loggers.
    """
    return lambda_logger
