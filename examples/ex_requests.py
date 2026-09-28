import requests

r = requests.get("https://www.scrapethissite.com/pages/simple/", timeout=20)
r.raise_for_status()
print(r.status_code, len(r.text), r.headers["content-type"])
