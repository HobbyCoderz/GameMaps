import sqlite3
import os

DB_PATH = os.path.join('data', 'gamemaps.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            map_path TEXT NOT NULL
        )
    ''')
    
    # Create markers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS markers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            title TEXT,
            note TEXT,
            type TEXT,
            game_coords TEXT,
            image_path TEXT,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == '__main__':
    init_db()
