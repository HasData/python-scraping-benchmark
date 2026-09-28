import json
import sys

import scrapy
from scrapy.crawler import CrawlerProcess

collected = []

SETTINGS = {
    "LOG_ENABLED": False,
    "ROBOTSTXT_OBEY": True,
    "DOWNLOAD_HANDLERS": {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    },
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
}


class TeamsSpider(scrapy.Spider):
    name = "teams"
    custom_settings = SETTINGS

    async def start(self):
        for p in range(1, 9):
            yield scrapy.Request(
                f"https://www.scrapethissite.com/pages/forms/?page_num={p}&per_page=25",
                meta={"playwright": True},
            )

    def parse(self, response):
        for tr in response.css("tr.team"):
            cells = tr.css("td::text").getall()
            collected.append({
                "name": cells[0].strip(),
                "year": cells[1].strip(),
                "wins": cells[2].strip(),
                "losses": cells[3].strip(),
            })


if len(sys.argv) > 1 and sys.argv[1] == "probe":
    probe_result = {}

    class ProbeSpider(scrapy.Spider):
        name = "probe"
        custom_settings = {**SETTINGS, "HTTPERROR_ALLOW_ALL": True}

        async def start(self):
            yield scrapy.Request("https://stackoverflow.com/questions",
                                 meta={"playwright": True})

        def parse(self, response):
            probe_result["status"] = response.status

    process = CrawlerProcess()
    process.crawl(ProbeSpider)
    process.start()
    print(json.dumps({"probe_status": probe_result.get("status", "no response (robots or error)")}))
    raise SystemExit(0)

process = CrawlerProcess()
process.crawl(TeamsSpider)
process.start()
print(json.dumps({"rows": len(collected[:200])}))
