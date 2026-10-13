import logging

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(processName)s %(name)s: %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Sets one log format for the whole service (also used inside grading processes)."""
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format=LOG_FORMAT, force=True)
    # pymongo is very chatty on DEBUG
    logging.getLogger("pymongo").setLevel(logging.WARNING)
