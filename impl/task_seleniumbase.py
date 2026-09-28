import json
import sys
import time

from seleniumbase import Driver

t0 = time.perf_counter()
driver = Driver(uc=True)
launch_s = round(time.perf_counter() - t0, 3)

if len(sys.argv) > 1 and sys.argv[1] == "probe":
    driver.uc_open_with_reconnect("https://stackoverflow.com/questions", 3)
    title = driver.title
    driver.quit()
    print(json.dumps({"probe_status": 200 if "Questions" in title else f"title: {title[:40]}"}))
    raise SystemExit(0)

rows = []
page = 1
while len(rows) < 200:
    driver.get(f"https://www.scrapethissite.com/pages/forms/?page_num={page}&per_page=25")
    for tr in driver.find_elements("css selector", "tr.team"):
        cells = tr.find_elements("tag name", "td")
        rows.append({
            "name": cells[0].text.strip(),
            "year": cells[1].text.strip(),
            "wins": cells[2].text.strip(),
            "losses": cells[3].text.strip(),
        })
    page += 1
driver.quit()

print(json.dumps({"rows": len(rows[:200]), "launch_s": launch_s}))
