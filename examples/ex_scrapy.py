import scrapy
from scrapy.crawler import CrawlerProcess

results = []

class CountriesSpider(scrapy.Spider):
    name = "countries"
    custom_settings = {"LOG_ENABLED": False, "ROBOTSTXT_OBEY": True}
    start_urls = ["https://www.scrapethissite.com/pages/simple/"]

    def parse(self, response):
        for c in response.css("div.country"):
            # in a real spider, yield the dict instead of appending
            results.append({
                "name": c.css("h3.country-name::text").getall()[-1].strip(),
                "capital": c.css("span.country-capital::text").get(),
            })

process = CrawlerProcess()
process.crawl(CountriesSpider)
process.start()
print(len(results), results[0])
