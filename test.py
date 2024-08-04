from seleniumwire import webdriver  # Import from seleniumwire

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

# Go to the Google home page
driver.get('https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&media_type=all&search_type=page&view_all_page_id=51212153078')

# Access requests via the `requests` attribute
for request in driver.requests:
    if request.response:
        print(
            request.url
        )