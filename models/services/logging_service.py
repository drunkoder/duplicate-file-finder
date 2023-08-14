import datetime
from models.enums import ActionType

from models.log_repository import Log
from models.log_repository import DB
from models.constants import CONSTANTS

class LogService:

    def __init__(self):
        self.db = DB('duplicate_files.db')

    def handle_select(self):
        logs = self.db.get_all_logs()
        return logs

    def handle_insert(self, action, location):
        message = ""
        timestamp = datetime.datetime.now().strftime(CONSTANTS.FORMAT_DATETIME_DB)
        if action == ActionType.DELETE:
            message = 'Deleted file '+ location
        elif action == ActionType.MOVE:
            message = 'Moved file '+ location
        else:
            message = 'Scanned directory '+ location
        log = Log(message, timestamp)
        self.db.insert_log(log)

    def handle_delete(self):
        self.db.clear_log()
