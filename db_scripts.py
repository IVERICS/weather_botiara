import sqlite3

connect = sqlite3.connect('database.db')
cursor = connect.cursor()
query = f'''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id TEXT, 
        lat TEXT,
        lon TEXT,
        full_name TEXT
        );'''
cursor.execute(query)
connect.commit()
connect.close()