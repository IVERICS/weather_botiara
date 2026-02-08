import sqlite3
from threading import Lock

USERS_TABLE = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL, 
        lat TEXT,
        lon TEXT,
        full_name TEXT
    );
'''

NOTIFICATIONS_TABLE = '''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        notification_time TEXT NOT NULL,
        description TEXT
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
'''

tables = {
    'users': USERS_TABLE,
    'notifications': NOTIFICATIONS_TABLE
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

    def execute_query(self, query, params=()):
        self.connect()
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f'❌ Ошибка выполнения запроса: {e}')
            return False

    def fetch_one(self, query, params=()):
        self.connect()
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f'❌ Ошибка получения данных: {e}')
            return None

    def fetch_all(self, query, params=()):
        self.connect()
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f'❌ Ошибка получения данных: {e}')
            return []
