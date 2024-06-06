from collections import Counter
from database.db_api import Database


def update_inverted_index(document_id, word_counts):
    with Database() as db:
        updates = [
            (word, document_id, count, count)
            for word, count in word_counts.items()
        ]
        db.executemany('''
                   INSERT INTO inverted_index (term, page_id, frequency)
                   VALUES (?, ?, ?)
                   ON CONFLICT(term, page_id) 
                   DO UPDATE SET frequency = frequency + ?
               ''', updates)


def index_document(document_id, tokens):
    word_counts = Counter(tokens)
    update_inverted_index(document_id, word_counts)


