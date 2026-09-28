import requests
from bs4 import BeautifulSoup

html = requests.get("https://www.scrapethissite.com/pages/simple/", timeout=20).text
soup = BeautifulSoup(html, "html.parser")
countries = soup.select("div.country")
first = countries[0]
print(len(countries), first.select_one("h3.country-name").get_text(strip=True))
