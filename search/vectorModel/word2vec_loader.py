import os

from gensim.models import KeyedVectors

_word2vec = None


def load_word2vec():
    global _word2vec
    if _word2vec is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'news.lowercased.lemmatized.word2vec.300d')
        _word2vec = KeyedVectors.load_word2vec_format(model_path, binary=False)
    return _word2vec
