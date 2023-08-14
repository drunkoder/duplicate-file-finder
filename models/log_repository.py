import sqlite3
from contextlib import closing


class Log:
    def __init__(self, message, timestamp):
        self.message = message
        self.timestamp = timestamp


class DB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row

    def ping(self):
        with closing(self.conn.cursor()) as cur:
            sql = "select 'ping' as col"
            resp = cur.execute(sql)
            for r in resp.fetchall():
                print(r['col'])

    def get_all_logs(self):
        with closing(self.conn.cursor()) as cur:
            sql = '''
                select message, timestamp from logs;
            '''
            logs = []
            rows = cur.execute(sql)
            for row in rows.fetchall():
                log = Log(row['message'], row['timestamp'])
                logs.append(log)
        return logs

    def insert_log(self, log):
        with closing(self.conn.cursor()) as cur:
            sql = '''
                insert into logs (message, timestamp)
                values (?, datetime('now','localtime'))
            '''
            cur.execute(sql, [log.message])
            self.conn.commit()

    def clear_log(self):
        with closing(self.conn.cursor()) as cur:
            sql = '''
                delete from logs
            '''
            cur.execute(sql)
            self.conn.commit()
