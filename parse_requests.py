import os
import time
import requests
from sqlalchemy.exc import IntegrityError
from parse_api.classes import Account, Ad
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from data.accounts import Account as ApiAccount
from data.jobqueue import Job
from data.advertisement import Advertisements
import datetime
from data import db_session


rename_filter = {
    'All Platforms': "",
    'Facebook': "&publisher_platforms[0]=facebook",
    'Instagram': "&publisher_platforms[0]=instagram",
    'Audience Network': "&publisher_platforms[0]=audience_network",
    'Messenger': "&publisher_platforms[0]=messenger",
    'All Types': "&media_type=all",
    'Image': "&media_type=image_and_meme",
    'Video': "&media_type=video"
}


# start
def parse_page(id: str, platform=None, media=None, ip=None, url=None):
    db_session.global_init("databases/accounts.db")
    if url is None:
        url_with_filters = \
            f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&" \
            f"view_all_page_id={id}{rename_filter[platform]}" \
            f"&sort_data[direction]=desc&" \
            f"sort_data[mode]=relevancy_monthly_grouped&search_type=page{rename_filter[media]}"
        db_sess = db_session.create_session()
        job = Job()
        job.account_id = id
        job.url = url_with_filters
        time_now = datetime.datetime.now().time()
        job.time = ":".join([str(time_now.hour), str(time_now.minute), str(time_now.second)])
        db_sess.add(job)
        db_sess.commit()
    else:
        url_with_filters = url
    # фильтры пользователя в filters
    url = f"https://www.facebook.com/ads/library/?active_status=all" \
          f"&ad_type=all&country=ALL&view_all_page_id={id}" \
          f"&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=page&media_type=all "
    account = Account(url)
    options = Options()
    # options.add_argument("--headless")
    # profile_directory = r'%AppData%\Mozilla\Firefox\Profiles\42ryon9o.adParseProf'
    # profile = webdriver.FirefoxProfile(os.path.expandvars(profile_directory))
    # options.profile = profile
    driver = webdriver.Firefox(options=options)
    driver.get(url_with_filters)
    try:
        _ = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='_7jvw x2izyaf x1hq5gj4 x1d52u69']")))
    except TimeoutError:
        print("empty account")
    time.sleep(1)
    account.name = driver.find_element(By.XPATH, "//div[@class='x8t9es0 x1ldc4aq x1xlr1w8 x1cgboj8 x4hq6eo xq9mrsl x1yc453h x1h4wwuj xeuugli']").text
    account.nickname = "@" + driver.find_elements(By.XPATH, "//a[@class='xt0psk2 x1hl2dhg xt0b8zv x8t9es0 x1fvot60 xxio538 xjnfcd9 xq9mrsl x1yc453h x1h4wwuj x1fcty0u']")[-1].get_attribute("href").split("/")[-1]
    account.image = driver.find_element(By.XPATH, "//img[@class='xl1xv1r x78zum5 x193iq5w x1us19tq xkrh0ho x1aqa79q x10btfu9 x1e152vy']").get_attribute("src")
    print(f"To Parse: {account.name}, {account.nickname}")
    footer = driver.find_element(By.XPATH, "//div[@class='xq4jnbd x78zum5 xdt5ytf xr1yuqi xkrivgy x4ii5y1 x1gryazu "
                                           "x1dr75xp xz9dl7a']")
    account.link = url_with_filters
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
        last_len = len(page_content)
        if len(page_content) > 1500 or count >= 20:
            break
        time.sleep(1)
        driver.execute_script('arguments[0].scrollIntoView(true)', footer)
    result = [Ad(element.get_attribute('innerHTML')) for element in page_content]
    account.ads = result.copy()
    account.total_ads = len(account.ads)
    print(f"Account total ads: {account.total_ads}")

    account.active_ads = account.count_active()
    driver.close()
    print(f"End {account.name}.")
    try:
        db_sess = db_session.create_session()
        api_account = ApiAccount()
        api_account.acc_id = account.id
        api_account.account_name = account.name
        api_account.account_username = account.nickname
        api_account.account_image = account.image
        api_account.account_totalAds = account.total_ads
        api_account.adlib_account_link = account.link
        api_account.account_activeAds = account.active_ads
        api_account.account_socialMedia_link = account.link
        db_sess.add(api_account)
        db_sess.commit()
    except IntegrityError:
        db_sess = db_session.create_session()
        record_to_update = db_sess.query(ApiAccount).filter(ApiAccount.acc_id == account.id).first()
        record_to_update.account_totalAds = account.total_ads
        record_to_update.account_activeAds = account.active_ads
        db_sess.commit()
        print(f"Account {account.name} already exists")

    db_sess = db_session.create_session()
    old_ads_id = db_sess.query(Advertisements.ad_id_another).all()
    old_ads_id = [ad[0] for ad in old_ads_id]
    for ad in account.ads:
        if int(ad.id) in old_ads_id:
            old_ad = db_sess.query(Advertisements).filter(Advertisements.ad_id_another == ad.id).first()
            old_ad_status = old_ad.ad_status
            if ad.status != old_ad_status:
                db_sess.delete(old_ad)
                api_ads = Advertisements()
                api_ads.ad_id_another = ad.id
                api_ads.ad_image = ad.image
                api_ads.ad_text = ad.text
                api_ads.ad_start_date = ad.start_date
                api_ads.ad_end_date = ad.end_date
                api_ads.ad_status = ad.status
                api_ads.ad_buttonStatus = ad.buttonText
                api_ads.ad_daysActive = ad.duration
                api_ads.ad_mediaType = ad.media_type
                api_ads.ad_landingLink = ad.landing
                api_ads.ad_downloadLink = ad.download
                api_ads.ad_platform = ad.platforms
                api_ads.account_id = account.id
                db_sess.add(api_ads)

        elif int(ad.id) not in old_ads_id:
            api_ads = Advertisements()
            api_ads.ad_id_another = ad.id
            api_ads.ad_image = ad.image
            api_ads.ad_text = ad.text
            api_ads.ad_start_date = ad.start_date
            api_ads.ad_end_date = ad.end_date
            api_ads.ad_status = ad.status
            api_ads.ad_buttonStatus = ad.buttonText
            api_ads.ad_daysActive = ad.duration
            api_ads.ad_mediaType = ad.media_type
            api_ads.ad_landingLink = ad.landing
            api_ads.ad_downloadLink = ad.download
            api_ads.ad_platform = ad.platforms
            api_ads.account_id = account.id
            db_sess.add(api_ads)

    db_sess.commit()
    requests.post(f"{ip}/refresh")
    print(f"Account {account.name} in database, refresh page")
