import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError, ConnectError


class MainSpiderSpider(scrapy.Spider):
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, errback=self.handle_errors)

    name = "main_spider"
    allowed_domains = ["itc.ua"]
    # start_urls = ["https://www.bbc.com/ukrainian"]
    start_urls = ["https://itc.ua/ua/",
                  "https://itc.ua/ua/ukrayina/",
                  "https://itc.ua/ua/tehnologiyi/",
                  "https://itc.ua/ua/nauka-ta-kosmos/",
                  "https://itc.ua/ua/tag/kriptovalyuta-ua/",
                  "https://itc.ua/ua/biznes-ua/",
                  "https://itc.ua/ua/pristroyi/",
                  "https://itc.ua/ua/soft/",
                  "https://itc.ua/ua/military-tech/",
                  "https://itc.ua/ua/avto-ua/",
                  "https://itc.ua/ua/igri/",
                  "https://itc.ua/ua/kino/",
                  "https://itc.ua/ua/oglyadi/oglyadi-partneriv/",
                  "https://itc.ua/ua/novini/",
                  "https://itc.ua/ua/oglyadi/",
                  "https://itc.ua/ua/statti/",
                  "https://itc.ua/ua/blogs/",
                  ]

    def parse(self, response, **kwargs):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if not content_type.startswith('text'):
            self.logger.info(f"Skipping non-text content: {response.url} (Content-Type: {content_type})")
            return
        links = [link.get() for link in response.css('a::attr(href)') if link.get().startswith('http')]
        if "/ua/" in response.url:
            title = response.css('title::text').get()

            text = ' '.join(
                response.xpath('''
                    //body//text()[
                        not(ancestor::script) and
                        not(ancestor::style) and
                        not(ancestor::nav) and
                        not(ancestor::header) and
                        not(ancestor::footer) and
                        not(ancestor::aside) and
                        not(ancestor::form) and 
                        not(ancestor::input) and 
                        not(ancestor::button) and
                        not(ancestor::a) and
                        not(ancestor-or-self::*[contains(@style, 'display: none') 
                                        or contains(@style, 'visibility: hidden')])
                    ]
                ''').getall()).strip()

            # повертаємо словник із зібраною інформацією
            yield {
                'url': response.url,
                'title': title,
                'text': text,
                'links': links
            }

        # перехід по знайденим посиланням для продовження краулінгу
        for link in links:
            if link.startswith('http') or link.startswith('https'):
                yield scrapy.Request(link, callback=self.parse, errback=self.handle_errors)
            else:
                self.logger.info(f"Знайдено не HTTP/HTTPS посилання: {link}")

    def handle_errors(self, failure):
        if failure.check(HttpError, DNSLookupError, TCPTimedOutError, ConnectError):
            # пропускаємо сайт та друкуємо інформацію про помилку
            self.logger.error('Request failed: %s', failure.request.url)
