import sqlite3
from threading import Lock

USERS_TABLE = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL, 
        lat TEXT,
        lon TEXT,
        notification_time TIMESTAMP,
        full_name TEXT
    );
'''

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
        if self.conn is None:
            self.conn = sqlite3.connect('./database/database.db')
            self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None

    def create_tables(self):
        self.connect()
        try:
            self.cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            existing_tables = [table[0] for table in self.cursor.fetchall()]
            for table_name, query in tables.items():
                if table_name not in existing_tables:
                    print(f'📦 Создаем таблицу: {table_name}')
                    self.cursor.execute(query)
            self.conn.commit()
            print('✅ Все таблицы готовы')
        except Exception as e:
            print(f'❌ Ошибка создания таблиц: {e}')
        finally:
            self.close()

