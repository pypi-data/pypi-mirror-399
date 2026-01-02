import logging
import logging.handlers


def setup_logger(
    fh_lev: int = logging.DEBUG, ch_lev: int = logging.ERROR
) -> logging.Logger:
    logger = logging.getLogger("pyVIN")
    logger.setLevel(logging.DEBUG)
    # create a file handler which logs even debug messages
    max_size = 2 * 1024 * 1024
    fh = logging.handlers.RotatingFileHandler(
        "pyVIN.log", maxBytes=max_size, backupCount=5
    )
    fh.setLevel(fh_lev)
    # create a console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(ch_lev)
    # create a formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
