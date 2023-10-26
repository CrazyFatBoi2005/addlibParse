
import pyautogui as pyautogui

import pickle
import time

from selenium.webdriver.common.by import By
#
# from selenium.webdriver.common.by import By
# # proxy_options = {
# #     "proxy": f"http://{login}:{password}@194.85.181.30:63966"
# # }
# options = webdriver.FirefoxOptions()
# options.add_argument("--no-sandbox")
#     # options.add_argument("--headless")
#
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                      f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
# driver = webdriver.Firefox(options=options)
# # driver.get('https://www.facebook.com/')
# # time.sleep(5)
# # with open("page.html", "w", encoding="utf-8") as f:
# #     f.write(driver.page_source)
#
# # name = driver.find_element(by=By.XPATH, value='//*[@id="email"]')
# # name.send_keys("+77477722006")
# # password = driver.find_element(by=By.XPATH, value='//*[@id="pass"]')
# # password.send_keys("lapa2174")
# # time.sleep(2)
# # pyautogui.press("Enter")
# driver.get("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=182714625642338&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=page&media_type=all")
# time.sleep(5)
# # driver.quit()
#
from seleniumwire import webdriver

# Определите URL прокси-сервера, логин и пароль
proxy_server_url = "http://aAnD9etY:5iYLwNwe@46.3.24.210:64358"

# Создайте опции для прокси
options = {
    'proxy': {
        'http': proxy_server_url,
        'https': proxy_server_url
    }
}

# Создайте экземпляр ChromeDriver с опциями прокси
driver = webdriver.Firefox(seleniumwire_options=options)
# driver.get("https://2ip.ru/")
driver.get("https://www.facebook.com/")


name = driver.find_element(by=By.XPATH, value='//*[@id="email"]')
name.send_keys("+77477722006")
password = driver.find_element(by=By.XPATH, value='//*[@id="pass"]')
password.send_keys("lapa2174")
time.sleep(2)
pyautogui.press("Enter")
time.sleep(5)
try:
    name1 = driver.find_element(by=By.XPATH, value='//*[@id="email"]')
    name1.send_keys("+77477722006")
    password1 = driver.find_element(by=By.XPATH, value='//*[@id="pass"]')
    password1.send_keys("lapa2174")
    time.sleep(2)
    sbm_btn = driver.find_element(by=By.ID, value="loginbutton")
    sbm_btn.click()
except:
    print(1)
time.sleep(15)

driver.get("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=182714625642338&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=page&media_type=all")
time.sleep(5)