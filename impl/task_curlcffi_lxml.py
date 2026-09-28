import json
import sys

from curl_cffi import requests as creq
from lxml import html

if len(sys.argv) > 1 and sys.argv[1] == "probe":
    r = creq.get("https://stackoverflow.com/questions", impersonate="chrome", timeout=20)
    print(json.dumps({"probe_status": r.status_code}))
    raise SystemExit(0)

rows = []
session = creq.Session(impersonate="chrome")
page = 1
while len(rows) < 200:
    r = session.get("https://www.scrapethissite.com/pages/forms/",
                    params={"page_num": page, "per_page": 25}, timeout=20)
    tree = html.fromstring(r.text)
    for tr in tree.xpath('//tr[@class="team"]'):
        cells = tr.xpath("./td/text()")
        rows.append({
            "name": cells[0].strip(),
            "year": cells[1].strip(),
            "wins": cells[2].strip(),
            "losses": cells[3].strip(),
        })
    page += 1

print(json.dumps({"rows": len(rows[:200])}))
