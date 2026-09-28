import urllib3

http = urllib3.PoolManager()
r = http.request("GET", "https://www.scrapethissite.com/pages/simple/", timeout=20.0)
print(r.status, len(r.data))
