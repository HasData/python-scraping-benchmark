from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.scrapethissite.com/pages/ajax-javascript/")
    page.click("a[id='2015']")
    page.wait_for_selector("td.film-title")
    titles = page.locator("td.film-title").all_inner_texts()
    browser.close()
print(len(titles), titles[0])
