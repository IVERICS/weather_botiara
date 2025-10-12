import sqlite3
from database.database import Database


class User:
    def __init__(self, telegram_id, full_name, lat, lon):
        self.users = []
        self.telegram_id = telegram_id
        self.full_name = full_name
        self.lat = lat
        self.lon = lon