import sqlite3
import os


class Database:
    def __init__(self, db_path='search_engine.db'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, 'database', db_path)
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def connect(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()

    def close(self):
        if self.connection:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()
            self.connection = None

    def execute(self, query, params=None):
        self.connect()
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)
        return self.cursor

    def executemany(self, query, params_list):
        self.connect()
        self.cursor.executemany(query, params_list)

    def commit(self):
        self.connection.commit()

    def get_pages_count(self):
        self.connect()
        return self.cursor.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
