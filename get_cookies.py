import pickle
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

options = Options()
# options.add_argument("--headless")
driver = webdriver.Edge(options=options)
driver.get("https://www.facebook.com/ads/library/?active_status=all&ad_type=political_and_issue_ads&country=KZ&media_type=all")
accept_button = driver.find_element(By.XPATH, "//button[@class='_42ft _4jy0 _al65 _4jy3 _4jy1 selected _51sy']")
accept_button.send_keys(Keys.ENTER)
time.sleep(5)
pickle.dump(driver.get_cookies(), open("cookies", "wb"))
time.sleep(2)