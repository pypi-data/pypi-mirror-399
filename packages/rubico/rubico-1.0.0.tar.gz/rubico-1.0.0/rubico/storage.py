import sqlite3
import threading

class Storage:
    def __init__(self, db_path="rubico.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._create_table()

    def _create_table(self):
        with self.lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    chat_id TEXT PRIMARY KEY,
                    data TEXT
                )
            """)
            self.conn.commit()

    def get(self, chat_id):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT data FROM users WHERE chat_id=?", (chat_id,))
            row = cur.fetchone()
            return eval(row[0]) if row else {}

    def set(self, chat_id, key, value):
        with self.lock:
            data = self.get(chat_id)
            data[key] = value
            self.conn.execute(
                "INSERT OR REPLACE INTO users(chat_id, data) VALUES(?,?)",
                (chat_id, str(data))
            )
            self.conn.commit()
