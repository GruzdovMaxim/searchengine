import subprocess
from database.setup_database import create_database
from search.IDF import calculate_idf
from search.page_rank import calculate_pagerank_nx
from search.vectorModel.word2vec_loader import load_word2vec
from search.vectorModel.vector_search import vectorize_all_documents
from web.app import app
import os
import sys
from dotenv import load_dotenv

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)

env_path = os.path.join(current_path, '.env')

if not os.path.exists(env_path):
    with open(env_path, 'w') as f:
        f.write(f"PYTHONPATH={current_path}\n")

load_dotenv(dotenv_path=env_path)

def run_crawler():
    subprocess.run(['scrapy', 'crawl', 'main_spider'], check=True, cwd='crawler')


def main():
    while True:
        print("\nДоступні команди:")
        print(" run-all - Запустити основні компоненти системи послідовно")
        print(" run-webapp - Запустити веб-додаток")
        print(" create-db - Створити базу даних")
        print(" run-spider - Запустити павука для збору даних")
        print(" pagerank - Розрахувати PageRank")
        print(" idf - Розрахувати IDF для термінів")
        print(" load-w2v - Завантажити модель Word2Vec")
        print(" vectorize-documents - Векторизувати всі документи")
        print(" quit - Завершити програму")

        user_input = input("Введіть команду: ")

        if user_input == "run-spider":
            run_crawler()
        elif user_input == "run-webapp":
            load_word2vec()
            app.run()
        elif user_input == "pagerank":
            calculate_pagerank_nx()
        elif user_input == "idf":
            calculate_idf()
        elif user_input == "load-w2v":
            load_word2vec()
        elif user_input == "vectorize-documents":
            vectorize_all_documents()
        elif user_input == "create-db":
            create_database()
        elif user_input == "run-all":
            create_database()
            run_crawler()
            calculate_idf()
            calculate_pagerank_nx()
            vectorize_all_documents()
        elif user_input == "quit":
            print("Програму завершено.")
            break
        else:
            print("Невідома команда.")


if __name__ == "__main__":
    main()
