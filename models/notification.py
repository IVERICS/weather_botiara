import sqlite3
from database.database import Database
from datetime import datetime


class Notification:
    def __init__(self, user_id, notification_time, description=None, id=None):
        self.user_id = user_id
        self.notification_time = notification_time
        self.description = description
        self.id = id

    def save_to_db(self):
        db = Database()
        try:
            print('notification 16')
            if self.id is None:
                print('notification 18')
                query = '''
                    INSERT INTO notifications (user_id, notification_time, description)
                    VALUES (?, ?, ?)
                '''
                params = (self.user_id, self.notification_time, self.description)
                if db.execute_query(query, params):
                    print('notification 25')
                    self.id = db.cursor.lastrowid
                    print(f'Уведомление создано с id: {self.id}')
                    return True
                return False
            else:
                print('notification 31')
                query = '''
                    UPDATE notifications
                    SET notification_time = ?, description = ?
                    WHERE id = ?
                '''
                params = (self.notification_time, self.description, self.id)
                return db.execute_query(query, params)

        except sqlite3.Error as e:
            print(f'❌ Ошибка сохранения уведомления: {e}')

    @classmethod
    def get_by_user_id(cls, user_id):
        db = Database()
        try:
            result = db.fetch_all(
                'SELECT * FROM notifications WHERE user_id = ?',
                (user_id,)
            )
            if result:
                return cls(
                    id=result[0],
                    user_id=result[1],
                    notification_time=cls._str_to_datetime(result[2]),
                    description=result[3]
                )
            return None
        except Exception as e:
            print(f'❌ Ошибка получения уведомления: {e}')
            return None

    @classmethod
    def get_all_with_notifications(cls):
        try:
            db = Database()
            query = '''
                SELECT 
                    n.*,
                    u.user_id as telegram_id,
                    u.full_name,
                    u.lat,
                    u.lon
                FROM notifications n
                JOIN users u ON n.user_id = u.id
                WHERE n.notification_time IS NOT NULL
                ORDER BY n.notification_time
            '''
            results = db.fetch_all(query)
            return results
        except Exception as e:
            print(f'❌ Ошибка получения уведомлений: {e}')
            return []

    def delete_from_db(self):
        if self.id is None:
            return False
        try:
            db = Database()
            query = '''DELETE FROM notifications WHERE id = ?'''
            return db.execute_query(query, (self.id,))
        except Exception as e:
            print(f'❌ Ошибка удаления уведомлений: {e}')
            return False

    @classmethod
    def delete_by_user_id(cls, user_id):
        try:
            db = Database()
            query = 'DELETE FROM notifications WHERE user_id = ?'
            return db.execute_query(query, (user_id,))
        except Exception as e:
            print(f'❌ Ошибка удаления уведомлений пользователя: {e}')
            return False

    @staticmethod
    def _str_to_datetime(date_str):
        if not date_str:
            return None
        try:
            if ':' in date_str and len('date_str') == 5:
                hours, minutes = map(int, date_str.split(':'))
                return datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            for fmt in ('%Y-%m-%d %H:%M:%S', '%H:%M:%S', '%H:%M'):
                try:
                    return datetime.strptime(date_str,fmt)
                except ValueError:
                    continue
            return None
        except Exception as e:
            print(f'❌ Ошибка преобразования даты: {e}')
            return None

    @staticmethod
    def _datetime_to_str(dt):
        if not dt:
            return None
        try:
            return dt.strftime('%H:%M')
        except Exception as e:
            print(f'❌ Ошибка преобразования datime в строку: {e}')
            return None

