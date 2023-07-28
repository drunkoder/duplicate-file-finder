import time
from models.constants import CONSTANTS


class FormatterExtensions:
    def format_size(size):
        for unit in CONSTANTS.FILESIZE_UNITS:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    def format_time(timestamp):
        return time.strftime(CONSTANTS.FORMAT_DATETIME, time.localtime(timestamp))