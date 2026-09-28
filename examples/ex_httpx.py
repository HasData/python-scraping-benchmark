import httpx

with httpx.Client(timeout=20) as client:
    r = client.get("https://www.scrapethissite.com/pages/simple/")
    r.raise_for_status()
    print(r.status_code, r.http_version, len(r.text))
