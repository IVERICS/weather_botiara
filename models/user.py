import sqlite3
from database.database import Database
from datetime import datetime
from models.notification import Notification


class User:
    def __init__(self, telegram_id, full_name, lat, lon, id=None):
        self.users = []
        self.telegram_id = telegram_id
        self.full_name = full_name
        self.lat = lat
        self.lon = lon
        self.id = id
        self._notification = None

    @property
    def notification_time(self):
        if self._notification is None:
            self._notification = Notification.delete_by_user_id(self.id)
        return self._notification.notification_time if self._notification else None


    @classmethod
    def get_by_telegram_id(cls, user_id):
        '''Получение пользователя по телеграмм айди'''
        db = Database()
        try:
            result = db.fetch_one('SELECT * FROM users WHERE user_id = ?', (user_id,))
            if result:
                user = cls(
                    id=result[0],
                    telegram_id=result[1],
                    lat=result[2],
                    lon=result[3],
                    full_name=result[4]
                )
                user._notification = Notification.get_by_user_id(user.id)
                return user
            return None
        except sqlite3.Error as e:
            print(f'❌ Ошибка получения пользователя: {e}')
            return None

    def safe_to_db(self):
        """
        Сохранение записи пользователя в базу данных
        Возвращает True при успехе, False при ошибке
        """
        db = Database()
        try:
            if self.id is None:
                query = """
                        INSERT INTO users (user_id, full_name, lat, lon)
                        VALUES (?, ?, ?, ?)
                        """
                params = (self.telegram_id, self.full_name, self.lat, self.lon)
                if db.execute_query(query, params):
                    self.id = db.cursor.lastrowid
                    print(f"✅ Пользователь создан с ID: {self.id}")
                    return True
                return False
            else:
                return self.update_in_db()
        except sqlite3.Error as e:
            print(f"❌ Ошибка сохранения пользователя: {e}")
            return False

    def update_in_db(self):
        """
        Обновление записи пользователя в базе данных
        Возвращает True при успехе, False при ошибке
        """
        if self.id is None:
            print("⚠️ Пользователь не имеет ID, используйте save_to_db() для создания")
            return False
        db = Database()
        try:
            query = """
                    UPDATE users
                    SET full_name = ?, lat = ?, lon = ?
                    WHERE id = ?
                    """
            params = (self.full_name, self.lat, self.lon, self.id)
            db.execute_query(query,params)
        except sqlite3.Error as e:
            print(f"❌ Ошибка обновления пользователя: {e}")
            return False

    def delite_from_db(self):
        """
        Удаление пользователя из базы данных
        """
        if self.id is None:
            print("⚠️ Пользователь не имеет ID")
            return False
        db = Database()
        try:
            db.cursor.execute("DELETE FROM users WHERE id = ?", (self.id,))
            db.conn.commit()
            if db.cursor.rowcount > 0:
                print(f"✅ Пользователь с ID: {self.id} удален")
                return True
            else:
                print(f"⚠️ Пользователь с ID: {self.id} не найден")
                return False
        except sqlite3.Error as e:
            print(f"❌ Ошибка удаления пользователя: {e}")
            return False

    def set_notification(self, notification_time=None):
        try:
            if notification_time is None:
                if self._notification:
                    success = self._notification.delete_from_db()
                    if success:
                        self._notification = None
                    return success
                return True
            else:
                if self._notification is None:
                    self._notification = Notification(user_id=self.id, notification_time=notification_time)
                else:
                    self._notification.notification_time = notification_time
                return self._notification.save_to_db()
        except Exception as e:
            print(f'❌ Ошибка установки уведомления: {e}')
            return False

    @classmethod
    def get_users_with_notification(cls, user_id=None):
        try:
            notifications_data = Notification.get_all_with_notifications()
            users = []
            for data in notifications_data:
                if user_id and str(user_id) != str(data[4]):
                    continue
                user = cls(
                    id=data[1],
                    telegram_id=data[4],
                    full_name=data[5],
                    lat=data[6],
                    lon=data[7],
                )
                user._notification = Notification(
                    id=data[0],
                    user_id=data[1],
                    notification_time=Notification._str_to_datetime(data[2])
                )
                users.append(user)
            return users
        except Exception as e:
            print(f"❌ Ошибка получения пользователей с уведомлением:{e}")
            return []
