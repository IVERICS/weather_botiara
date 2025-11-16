import sqlite3
from database.database import Database
from datetime import datetime


class User:
    def __init__(self, telegram_id, full_name, lat, lon):
        self.users = []
        self.telegram_id = telegram_id
        self.full_name = full_name
        self.lat = lat
        self.lon = lon
        self.id = None
        self.notification_time = None

    def safe_to_db(self):
        """
        Сохранение записи пользователя в базу данных
        Возвращает True при успехе, False при ошибке
        """
        db = Database()
        db.connect()
        try:
            if self.id is None:
                query = """
                        INSERT INTO users (user_id, full_name, lat, lon)
                        VALUES (?, ?, ?, ?)
                        """
                params = (self.telegram_id, self.full_name, self.lat, self.lon)
                db.cursor.execute(query, params)
                self.id = db.cursor.lastrowid
                db.conn.commit()
                print(f"✅ Пользователь создан с ID: {self.id}")
                return True
            else:
                return self.update_in_db()
        except sqlite3.Error as e:
            print(f"❌ Ошибка сохранения пользователя: {e}")
            return False
        finally:
            db.close()

    def update_in_db(self):
        """
        Обновление записи пользователя в базе данных
        Возвращает True при успехе, False при ошибке
        """
        if self.id is None:
            print("⚠️ Пользователь не имеет ID, используйте save_to_db() для создания")
            return False
        db = Database()
        db.connect()
        try:
            query = """
                    UPDATE users
                    SET user_id = ?, full_name = ?, lat = ?, lon = ?
                    WHERE id = ?
                    """
            params = (self.telegram_id, self.full_name, self.lat, self.lon, self.id)
            db.cursor.execute(query,params)
            db.conn.commit()
            if db.cursor.rowcount > 0:
                print(f"✅ Пользователь с ID: {self.id} обновлен")
                return True
            else:
                print(f"⚠️ Пользователь с ID: {self.id} не найден")
                return False
        except sqlite3.Error as e:
            print(f"❌ Ошибка обновления пользователя: {e}")
            return False
        finally:
            db.close()

    def delite_from_db(self):
        """
        Удаление пользователя из базы данных
        """
        if self.id is None:
            print("⚠️ Пользователь не имеет ID")
            return False
        db = Database()
        db.connect()
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
        finally:
            db.close()

    def set_notification(self, notification_time=None):
        self.notification_time = notification_time
        return self.update_in_db()

    @classmethod
    def get_users_with_notification(cls, user_id=None):
        db = Database()
        db.connect()
        try:
            if user_id is None:
                query = '''
                    SELECT * FROM users
                    WHERE notification_time IS NOT NULL
                    ORDER BY notification_time
                '''
                params = ()
            else:
                query = '''
                            SELECT * FROM users
                            WHERE notification_time IS NOT NULL AND user_id = ?
                            ORDER BY notification_time
                        '''
                params = (user_id,)
            db.cursor.execute(query, params)
            rows = db.cursor.fetchall()
            return [cls._create_from_row(row) for row in rows if row]
        except Exception as e:
            print(f"❌ Ошибка получения пользователя с уведомлением:{e}")
            return []
        finally:
            db.close()

    @classmethod
    def _create_from_row(cls, row):
        '''Создание объекта user из строки БД'''
        try:
            if hasattr(row,'_fields'):
                row_dict = {key: row[key] for key in row.keys()}
            else:
                columns = ['id', 'user_id', 'lat', 'lon', 'notification_time', 'full_name']
                row_dict = dict(zip(columns, row))
            user = cls.__new__(cls)
            user.id = row_dict['id']
            user.user_id = row_dict['user_id']
            user.lat = row_dict.get('lat', '')
            user.lon = row_dict.get('lon', '')
            user.notification_time = cls._parse_datetime(row_dict.get('notification_time'))
            user.full_name = row_dict.get('full_name', '')
            return user
        except Exception as e:
            print(f"❌ Ошибка cоздания пользователя: {e}")
            return None

    @staticmethod
    def _parse_datetime(date_str):
        '''Парсинг строки даты из БД'''
        if not date_str:
            return None
        try:
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S.%f'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            print(f"❌ Ошибка парсинга даты '{date_str}': {e}")
            return None
