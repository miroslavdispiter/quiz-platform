from enum import Enum


class ResultStatus(str, Enum):
    PROCESSING = "PROCESSING"  # answers are being processed in a separate process
    DONE = "DONE"              # points are calculated and saved
