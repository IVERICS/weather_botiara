import sqlite3
from threading import Lock

USERS_TABLE = '''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL, 
        lat TEXT,
        lon TEXT,
        full_name TEXT
        );'''

tables = {
    'users': USERS_TABLE,
}


class Singleton(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=Singleton):
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect('./database.db')
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def create_tables(self):
        self.connect()
        names = []
        for name in self.cursor.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
            names.append(name[0])
        for table_name, query in tables.items():
            if table_name not in names:
                self.cursor.execute(query)
        self.close()

