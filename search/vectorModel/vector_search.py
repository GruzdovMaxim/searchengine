import numpy as np
from scipy.spatial.distance import cosine
from database.db_api import Database
from indexer.text_processing import tokenize, normalize
from search.vectorModel.word2vec_loader import load_word2vec


def vectorize_all_documents():
    word2vec = load_word2vec()
    with Database() as db:
        pages = db.execute("SELECT id, content FROM pages WHERE vector IS NULL").fetchall()
        updates = []
        for page_id, content in pages:
            vector = document_to_vector(content, word2vec).astype(np.float32).tobytes()
            updates.append((vector, page_id))
        db.executemany("UPDATE pages SET vector = ? WHERE id = ?", updates)
        db.commit()


def document_to_vector(text, word2vec):
    tokens = tokenize(normalize(text))
    word_vectors = [word2vec[word] for word in tokens if word in word2vec]
    if not word_vectors:
        return np.zeros(word2vec.vector_size)

    # num_known_words = len(word_vectors)
    # num_total_words = len(tokens)
    # known_word_ratio = num_known_words / num_total_words
    # print(f"Document known word ratio: {known_word_ratio:.2%}")

    return np.mean(word_vectors, axis=0)


def vector_search(query):
    word2vec = load_word2vec()
    query_vector = document_to_vector(query, word2vec)

    results = {}
    with Database() as db:
        rows = db.execute("SELECT id, vector FROM pages WHERE vector IS NOT NULL").fetchall()
        for page_id, vector_blob in rows:
            doc_vector = np.frombuffer(vector_blob, dtype=np.float32)
            similarity = 1 - cosine(query_vector, doc_vector)
            if similarity >= 0:
                normalized_score = normalize_score(similarity)
                results[page_id] = normalized_score

    return results


def normalize_score(score, max_score= 1, min_score=0):
    return 100 * (score - min_score) / (max_score - min_score)
