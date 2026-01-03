import sqlite3, json, threading

class Storage:
    def __init__(self, path="rubico.db"):
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init()

    def _init(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT PRIMARY KEY,
            data TEXT
        )
        """)
        self.conn.commit()

    def get(self, chat_id):
        cur = self.conn.execute("SELECT data FROM users WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else {}

    def set(self, chat_id, key, value):
        data = self.get(chat_id)
        data[key] = value
        self.conn.execute(
            "INSERT OR REPLACE INTO users VALUES (?,?)",
            (chat_id, json.dumps(data))
        )
        self.conn.commit()
