from contextlib import closing
import sqlite3

from models.constants import CONSTANTS

class FileRepository:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(CONSTANTS.DATABASE_FILENAME)
        self.conn.row_factory = sqlite3.Row


    def insert(self, file_path, file_hash):
        with closing(self.conn.cursor()) as cur:
            sql ="INSERT INTO duplicates (file_path, hash) VALUES (?, ?)"
            self.cursor.execute(sql, (file_path, file_hash))
            self.conn.commit()

            return cur.rowcount > 0