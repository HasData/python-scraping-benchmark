import requests
from lxml import html

page = requests.get("https://www.scrapethissite.com/pages/simple/", timeout=20).text
tree = html.fromstring(page)
names = tree.xpath("//h3[@class='country-name']/text()[normalize-space()]")
capitals = tree.xpath("//span[@class='country-capital']/text()")
print(len(capitals), names[0].strip(), capitals[0])
