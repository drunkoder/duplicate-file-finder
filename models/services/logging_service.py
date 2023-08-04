import datetime

from models.log_repository import Log
from models.log_repository import DB
from models.constants import CONSTANTS

class LogService:

    def __init__(self):
        self.db = DB('duplicate_files.db')
    def handle_select(self):
        logs = self.db.get_all_logs()
        for l in logs:
            print(l)

    def handle_insert(self, action, location):
        message = ""
        timestamp = datetime.datetime.now().strftime(CONSTANTS.FORMAT_DATETIME_DB)
        if action == 'delete':
            message = 'Deleted file '+ location
        else:
            message = 'Scanned directory '+ location
        log = Log(message, timestamp)
        self.db.insert_log(log)