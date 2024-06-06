# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exceptions import DropItem
from indexer.indexer import index_document
from indexer.text_processing import normalize, tokenize
from database.db_api import Database


class CrawlerPipeline:
    def __init__(self):
        self.db = None

    def open_spider(self, spider):
        self.db = Database() 
        self.db.connect()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        if not item['text'].strip():
            # Пропустити збереження, якщо контент відсутній
            raise DropItem("Missing content on page %s" % item['url'])

        text = normalize(item['text'])
        tokens = tokenize(text)
        word_counts = len(tokens)
        if word_counts < 10:
            # Пропустити збереження, якщо контента мало
            raise DropItem("Text is too small on page %s" % item['url'])

        print(f"adding {item['url']}")
        self.db.execute('''
                    INSERT OR IGNORE INTO pages (url, content, title, words_count, raw_content)
                    VALUES (?, ?, ?, ?, ?)
                ''', (item['url'], text, item['title'], word_counts, item['text']))

        if self.db.cursor.rowcount == 0:
            self.db.commit()
            return None

        page_id = self.db.cursor.lastrowid  # отримання останнього ID через запит

        links = [
            (page_id, link)
            for link in item.get('links', [])
        ]

        self.db.executemany('''
                    INSERT OR IGNORE INTO links (source_page_id, target_url)
                    VALUES (?, ?)
                ''', links)
        self.db.commit()

        index_document(page_id, tokens)

        return item
