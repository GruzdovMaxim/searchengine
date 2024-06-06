import os
from nltk.tokenize import word_tokenize
import pymorphy2
import re
from spacy.lang.uk import Ukrainian

stop_words = set()
nlp = Ukrainian()
morph = pymorphy2.MorphAnalyzer(lang='uk')


def load_stopwords(file_name):
    global stop_words
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        stop_words = set(file.read().splitlines())


def normalize(text):
    global stop_words

    if not stop_words:
        load_stopwords('stopwords_ua.txt')

    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = text.lower()
    tokens = word_tokenize(text)

    normalized_words = []
    for token in tokens:
        if token.isalpha() and token not in stop_words:
            parsed_token = morph.parse(token)[0]
            normalized_token = parsed_token.normal_form
            normalized_words.append(normalized_token)

    normalized_text = ' '.join(normalized_words)

    return normalized_text


def tokenize(text):
    return word_tokenize(text)


# textt = "Це приклад тексту для нормалізації. Тут є деякі стоп-слова та цифри, наприклад 123 😊."
# normalized_textt = normalize(textt)
# print(normalized_textt)
