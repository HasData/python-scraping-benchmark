from curl_cffi import requests

# The impersonate flag is the library's point: the TLS handshake and header
# order match a real Chrome. The bench's probe column records what that wins
# on a protected page at any given date.
r = requests.get(
    "https://www.scrapethissite.com/pages/simple/",
    impersonate="chrome",
    timeout=20,
)
print(r.status_code, len(r.text))
