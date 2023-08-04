from contextlib import closing
import sqlite3

from models.constants import CONSTANTS

class Migration:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(CONSTANTS.DATABASE_FILENAME)

    def createSchema(self):
        self.createTblDuplicates()

    def createTblDuplicates(self):
        # Create the 'duplicates' table in the database if it doesn't exist
         with closing(self.conn.cursor()) as cur:
            sql ="""
                    CREATE TABLE IF NOT EXISTS duplicates (
                        id INTEGER PRIMARY KEY,
                        file_path TEXT UNIQUE,
                        hash TEXT
                    )
                    
                    CREATE TABLE IF NOT EXISTS logs(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         message TEXT NOT NULL,
                         timestamp DATETIME NOT NULL
                    );
                """
            cur.execute(sql)
            self.conn.commit()
