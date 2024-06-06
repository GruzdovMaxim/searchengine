import sqlite3
import os


def create_database():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    database_dir = os.path.join(base_dir, 'database')
    db_path = os.path.join(database_dir, 'search_engine.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS pages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            content TEXT,
            raw_content TEXT,
            title TEXT,
            words_count INTEGER,
            page_rank REAL DEFAULT 0.0,
            rank_group TEXT,
            vector BLOB
        );
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS inverted_index (
            term TEXT,
            page_id INTEGER,
            frequency INTEGER,    
            PRIMARY KEY (term, page_id),
            FOREIGN KEY (page_id) REFERENCES pages (id)
        );
    ''')

    c.execute('''
             CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY,
                source_page_id INTEGER,
                target_url TEXT,
                FOREIGN KEY (source_page_id) REFERENCES pages (id)
            );
        ''')

    c.execute("""
           CREATE TABLE IF NOT EXISTS term_idf (
               term TEXT PRIMARY KEY,
               idf REAL,
               UNIQUE(term)
           );
       """)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database()
