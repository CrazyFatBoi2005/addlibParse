import time
from parse_api.classes import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

nike_url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id" \
           "=15087023444&search_type=page&media_type=all "


# start
def parse_page(url: str, filters: dict):

    account = Account(url)
    driver = webdriver.Edge()
    driver.get(url)
    _ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='xh8yej3']")))
    time.sleep(2)
    account.name = driver.find_element(By.XPATH, "//div[@class='x8t9es0 x1ldc4aq x1xlr1w8 x1cgboj8 x4hq6eo xq9mrsl x1yc453h x1h4wwuj xeuugli']").text
    account.nickname = "@" + driver.find_elements(By.XPATH, "//a[@class='xt0psk2 x1hl2dhg xt0b8zv x8t9es0 x1fvot60 xxio538 xjnfcd9 xq9mrsl x1yc453h x1h4wwuj x1fcty0u']")[-1].get_attribute("href").split("/")[-1]
    account.image = driver.find_element(By.XPATH, "//img[@class='xl1xv1r x78zum5 x193iq5w x1us19tq xkrh0ho x1aqa79q x10btfu9 x1e152vy']").get_attribute("src")
    print(account.name)
    print(account.nickname)
    footer = driver.find_element(By.XPATH, "//div[@class='xq4jnbd x78zum5 xdt5ytf xr1yuqi xkrivgy x4ii5y1 x1gryazu "
                                           "x1dr75xp xz9dl7a']")
    last_len = 0
    count = 0
    while True:
        # get content
        page_content = driver.find_elements(By.XPATH, "//div[@class='_7jvw x2izyaf x1hq5gj4 x1d52u69']")
        if last_len == len(page_content):
            count += 1
        else:
            count = 0
        # scroll down
        print(count)
        last_len = len(page_content)
        if len(page_content) > 300 or count >= 5:
            break
        time.sleep(1)
        driver.execute_script('arguments[0].scrollIntoView(true)', footer)

    result = [Ad(element.get_attribute('innerHTML')) for element in page_content]
    account.ads = result.copy()
    account.total_ads = len(account.ads)
    # print
    for i in result:
        print("\n".join(i.get_data()))
        print()

    account.active_ads = account.count_active()
    print(account.get_data())
    driver.close()
    return account
