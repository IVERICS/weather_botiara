import sqlite3
from database.database import Database


class User:
    def __init__(self, telegram_id, full_name, lat, lon):
        self.users = []
        self.telegram_id = telegram_id
        self.full_name = full_name
        self.lat = lat
        self.lon = lon
        self.id = None

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
