import httpx
from parsel import Selector

html = httpx.get("https://www.scrapethissite.com/pages/simple/", timeout=20).text
sel = Selector(text=html)
rows = [
    {
        "name": c.css("h3.country-name::text").getall()[-1].strip(),
        "capital": c.css("span.country-capital::text").get(),
        "population": c.xpath(".//span[@class='country-population']/text()").get(),
    }
    for c in sel.css("div.country")
]
print(len(rows), rows[0])
