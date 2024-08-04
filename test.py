from seleniumwire import webdriver
from selenium.webdriver.common.by import By
import time

# Launch the browser with SeleniumWire capabilities
driver = webdriver.Chrome()

# Perform actions to trigger XHR requests
driver.get("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id=103995336066375&search_type=page&media_type=all")
driver.maximize_window()

# search_bar = driver.find_element(By.ID, "a-autoid-4-announce")
# search_bar.click()

# Wait for a short time to ensure XHR requests have been triggered
time.sleep(5)

# Access requests via the `requests` attribute
for request in driver.requests:
    if request.response:
        print(f"URL: {request.url}")
        print(f"Method: {request.response.body.decode('utf-8')}")
        print(f"Response Status Code: {request.response.status_code}")