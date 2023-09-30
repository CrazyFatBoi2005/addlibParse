import time
from classes import *
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

nike_url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id" \
           "=15087023444&search_type=page&media_type=all "

# start
driver = webdriver.Edge()
driver.get(nike_url)
_ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='xh8yej3']")))
page_content = []
footer = driver.find_element(By.XPATH, "//div[@class='xq4jnbd x78zum5 xdt5ytf xr1yuqi xkrivgy x4ii5y1 x1gryazu "
                                            "x1dr75xp xz9dl7a']")
while True:
    try:
        loadingIcon = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//svg[@class='x1ka1v4i x7v9bd0 x1esw782 xa4qsjk xxymvpz']")))
        time.sleep(1)
        driver.execute_script('arguments[0].scrollIntoView(true)', footer)
    except:
        # get content
        page_content = driver.find_elements(By.XPATH, "//div[@class='_7jvw x2izyaf x1hq5gj4 x1d52u69']")
        # scroll down
        driver.execute_script('arguments[0].scrollIntoView(true)', footer)
        if len(page_content) > 300:
            break


result = [Ad(element.get_attribute('innerHTML')) for element in page_content]
# print
for i in result:
    print("\n".join(i.get_data()))
    print()
time.sleep(1000)
driver.close()
