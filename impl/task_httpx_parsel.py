import json
import sys

import httpx
from parsel import Selector

if len(sys.argv) > 1 and sys.argv[1] == "probe":
    r = httpx.get("https://stackoverflow.com/questions",
                  headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"}, timeout=20, follow_redirects=True)
    print(json.dumps({"probe_status": r.status_code}))
    raise SystemExit(0)

rows = []
with httpx.Client(timeout=20) as client:
    page = 1
    while len(rows) < 200:
        r = client.get("https://www.scrapethissite.com/pages/forms/",
                       params={"page_num": page, "per_page": 25})
        sel = Selector(text=r.text)
        for tr in sel.css("tr.team"):
            cells = tr.css("td::text").getall()
            rows.append({
                "name": cells[0].strip(),
                "year": cells[1].strip(),
                "wins": cells[2].strip(),
                "losses": cells[3].strip(),
            })
        page += 1

print(json.dumps({"rows": len(rows[:200])}))
