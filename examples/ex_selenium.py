from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)
driver.get("https://www.scrapethissite.com/pages/ajax-javascript/")
driver.find_element(By.ID, "2015").click()
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "td.film-title"))
)
titles = [el.text for el in driver.find_elements(By.CSS_SELECTOR, "td.film-title")]
driver.quit()
print(len(titles), titles[0])
