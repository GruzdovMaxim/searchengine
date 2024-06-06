import math
from database.db_api import Database
from indexer.text_processing import normalize, tokenize
from collections import defaultdict


def bm25_search(query, k1=2, b=0.75):
    query_terms = tokenize(normalize(query))
    if not query_terms:
        return {}
    
    with Database() as db:
        words_count = db.execute("SELECT id, words_count FROM pages")
        doc_lengths = {row[0]: row[1] for row in words_count}
        total_length = sum(doc_lengths.values())
        total_docs = len(doc_lengths)
        average_length = total_length / total_docs if total_docs else 0

        cursor = db.execute("SELECT term, idf FROM term_idf WHERE term IN ({})"
                            .format(','.join('?' * len(query_terms))), query_terms)

        idf_scores = dict(cursor.fetchall())

        doc_scores = defaultdict(float)
        for term in query_terms:
            if term in idf_scores:
                term_query = "SELECT page_id, frequency FROM inverted_index WHERE term = ?"
                term_data = db.execute(term_query, (term,))
                idf = idf_scores[term]

                for doc_id, freq in term_data:
                    words_count = doc_lengths[doc_id]
                    tf = (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * (words_count / average_length)))
                    # doc_scores[doc_id] += idf * tf
                    doc_scores[doc_id] += normalize_score(idf * tf, total_docs, len(query_terms), average_length, k1)

    return dict(doc_scores)


def normalize_score(score, total_docs, query_len, avl, k1, word_max_frequency=0.10):
    idf = math.log((total_docs - 1 + 0.5) / (1 + 0.5) + 1)
    tf = word_max_frequency * avl * k1 / (word_max_frequency * avl + k1)
    max_score = tf * idf * query_len
    return 100 * score / max_score
