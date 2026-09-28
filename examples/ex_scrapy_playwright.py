# On Windows the twisted + playwright teardown prints a harmless
# "Event loop is closed" after the results, a known upstream wart.
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod

results = []

class FilmsSpider(scrapy.Spider):
    name = "films"
    custom_settings = {
        "LOG_ENABLED": False,
        "ROBOTSTXT_OBEY": True,
        # route downloads through Playwright, keep everything else Scrapy
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    async def start(self):
        yield scrapy.Request(
            "https://www.scrapethissite.com/pages/ajax-javascript/",
            meta={"playwright": True, "playwright_page_methods": [
                PageMethod("click", "a[id='2015']"),
                PageMethod("wait_for_selector", "td.film-title"),
            ]},
        )

    def parse(self, response):
        results.extend(t.strip() for t in response.css("td.film-title::text").getall())

process = CrawlerProcess()
process.crawl(FilmsSpider)
process.start()
print(len(results), results[0] if results else None)
