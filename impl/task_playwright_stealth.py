import json
import sys
import time

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

with sync_playwright() as p:
    t0 = time.perf_counter()
    browser = p.chromium.launch(headless=True)
    page_obj = browser.new_page()
    Stealth().apply_stealth_sync(page_obj)
    launch_s = round(time.perf_counter() - t0, 3)

    if len(sys.argv) > 1 and sys.argv[1] == "probe":
        resp = page_obj.goto("https://stackoverflow.com/questions")
        print(json.dumps({"probe_status": resp.status}))
        browser.close()
        raise SystemExit(0)

    rows = []
    page = 1
    while len(rows) < 200:
        page_obj.goto(f"https://www.scrapethissite.com/pages/forms/?page_num={page}&per_page=25")
        for tr in page_obj.query_selector_all("tr.team"):
            cells = tr.query_selector_all("td")
            rows.append({
                "name": cells[0].inner_text().strip(),
                "year": cells[1].inner_text().strip(),
                "wins": cells[2].inner_text().strip(),
                "losses": cells[3].inner_text().strip(),
            })
        page += 1
    browser.close()

print(json.dumps({"rows": len(rows[:200]), "launch_s": launch_s}))
