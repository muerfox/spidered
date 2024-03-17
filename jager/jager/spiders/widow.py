import scrapy
import random
from urllib.parse import urlparse

class BlackWidow(scrapy.Spider):
    name = 'widow'
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
    ]
    avoid_extensions = ['.jpg', '.png', '.gif', '.pdf', '.ico', '.css', '.woff', '.woff2', '.ttf', '.otf', '.webp', '.svg']

    def start_requests(self):
        url = getattr(self, 'url', None)
        if url:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        headers_dict = {}
        for name, value in response.headers.items():
            if isinstance(value, list):
                headers_dict[name.decode()] = [v.decode() for v in value]
            else:
                headers_dict[name.decode()] = value.decode()

        body = response.body.decode(response.encoding)

        extracted_urls = self.extract_urls(response)

        yield {
            'url': response.url,
            'headers': headers_dict,
            'body': body,
            'extracted_urls': extracted_urls
        }

        original_domain = urlparse(response.url).netloc

        for url in extracted_urls:
            current_domain = urlparse(url).netloc
            if not any(url.endswith(ext) for ext in self.avoid_extensions):
                if original_domain == current_domain:
                    yield scrapy.Request(url=url, callback=self.parse)

    def extract_urls(self, response):
        urls = []
        urls.extend(response.css('script::attr(src)').extract())
        urls.extend(response.css('link[rel="stylesheet"]::attr(href)').extract())
        urls.extend(response.css('img::attr(src)').extract())
        urls.extend(response.css('iframe::attr(src)').extract())
        urls.extend(response.css('form::attr(action)').extract())
        urls.extend(response.css('object::attr(data)').extract())
        urls.extend(response.css('embed::attr(src)').extract())
        urls.extend(response.css('a::attr(href)').extract())
        urls = list(set(urls))
        return urls

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BlackWidow, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.use_random_user_agent, signal=scrapy.signals.spider_opened)
        return spider

    def use_random_user_agent(self):
        self.user_agent = random.choice(self.user_agents)
