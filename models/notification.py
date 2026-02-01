import sqlite3
from database.database import Database
from datetime import time


class Notification:
    def __init__(self, user_id, notification_time, description=None):
        self.user_id = user_id,
        self.notification_time = notification_time,
        self.description = description
        self.id = None

    def save_to_db(self):
        db = Database()
        db.connect()
        try:
            query = '''
                INSERT INTO notifications (user_id, notifications_time, description)
                VALUES (?, ?, ?)
            '''
            params = (self.user_id, self.notification_time, self.description)
            db.cursor.execute(query, params)
            self.id = db.cursor.lastrowid
            db.conn.commit()
            print(f'Уведомление создано с id: {self.id}')
        except sqlite3.Error as e:
            print(f'❌ Ошибка сохранения уведомления: {e}')
        finally:
            db.close()