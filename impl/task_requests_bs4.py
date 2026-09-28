import json
import sys

import requests
from bs4 import BeautifulSoup

if len(sys.argv) > 1 and sys.argv[1] == "probe":
    r = requests.get("https://stackoverflow.com/questions",
                     headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"},
                     timeout=20)
    print(json.dumps({"probe_status": r.status_code}))
    raise SystemExit(0)

rows = []
session = requests.Session()
page = 1
while len(rows) < 200:
    r = session.get("https://www.scrapethissite.com/pages/forms/",
                    params={"page_num": page, "per_page": 25}, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    for tr in soup.select("tr.team"):
        cells = tr.select("td")
        rows.append({
            "name": cells[0].get_text(strip=True),
            "year": cells[1].get_text(strip=True),
            "wins": cells[2].get_text(strip=True),
            "losses": cells[3].get_text(strip=True),
        })
    page += 1

print(json.dumps({"rows": len(rows[:200])}))
