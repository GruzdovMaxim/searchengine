import math
from database.db_api import Database


def calculate_idf():
    with Database() as db:
        total_docs = db.get_pages_count()
        # отримання частоти документів для кожного терміну
        term_data = db.execute("SELECT term, COUNT(DISTINCT page_id) as doc_freq FROM inverted_index GROUP BY term")\
            .fetchall()

        updates = []
        for term, doc_freq in term_data:
            idf = math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
            updates.append((idf, term))

        db.executemany("INSERT OR REPLACE INTO term_idf (idf, term) VALUES (?, ?)", updates)
