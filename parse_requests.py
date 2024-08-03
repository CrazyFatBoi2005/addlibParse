import json
import os
import time
import zipfile
from zipfile import ZipFile

import requests
from botocore.exceptions import NoCredentialsError
from sqlalchemy.exc import IntegrityError
from parse_api.classes import Account, Ad
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from data.accounts import Account as ApiAccount
from data.groups import Group as ApiGroup
from data.jobqueue import Job
from data.advertisement import Advertisements
import datetime
from data import db_session

import boto3
from botocore.client import Config
from io import BytesIO


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


s3 = boto3.resource(
        's3',
        endpoint_url='https://s3.timeweb.com',
        region_name='ru-1',
        aws_access_key_id='it27776',
        aws_secret_access_key='1cad6c15403631a01cc0bf26a5ce1524',
        config=Config(s3={'addressing_style': 'path'})
    )

s3_client = boto3.client(
    's3',
    endpoint_url='https://s3.timeweb.com',
    region_name='ru-1',
    aws_access_key_id='it27776',
    aws_secret_access_key='1cad6c15403631a01cc0bf26a5ce1524',
    config=Config(s3={'addressing_style': 'path'})
)

bucket_name = "7b3ae2a6-1e521fbf-430f-4275-aea8-858d0059469b"
bucket_obj = s3.Bucket(bucket_name)


def download_zip_from_s3(s3_key, account_name, status):
    try:
        if status == "Active":
            s3_client.download_file(bucket_name, s3_key, f"temporary_zips/{account_name}_active_media.zip")
        else:
            s3_client.download_file(bucket_name, s3_key, f"temporary_zips/{account_name}_inactive_media.zip")
        return "OK"
    except:
        return None


def modify_zip(zip_data, additional_files):
    with zipfile.ZipFile(zip_data, 'a') as original_zip:
        for file_path, file_content in additional_files.items():
            original_zip.writestr(file_path, file_content)


def upload_zip_to_s3(updated_zip_path, s3_path):
    s3_client.upload_file(updated_zip_path, bucket_name, s3_path)


# start
def parse_page(id_: str, group_id: int, platform=None, media=None, ip=None, url=None):
    db_session.global_init("databases/accounts.db")
    if url is None:
        url_with_filters = \
            f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&" \
            f"view_all_page_id={id_}{rename_filter.get(platform, '')}" \
            f"&sort_data[direction]=desc&" \
            f"sort_data[mode]=relevancy_monthly_grouped&search_type=page{rename_filter[media]}"
        db_sess = db_session.create_session()
        old_job = db_sess.query(Job).filter(Job.account_id == id_).first()
        if old_job is None:
            job = Job()
            job.account_id = id_
            job.url = url_with_filters
            time_now = datetime.datetime.now().time()
            job.time = ":".join([str(time_now.hour), str(time_now.minute), str(time_now.second)])
            db_sess.add(job)
            db_sess.commit()
    else:
        url_with_filters = url
    # фильтры пользователя в filters
    # url = f"https://www.facebook.com/ads/library/?active_status=all" \
    #       f"&ad_type=all&country=ALL&view_all_page_id={id}" \
    #       f"&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=page&media_type=all "
    # account = Account(url)
    account = Account(url_with_filters)
    # options.add_argument("--headless")
    # profile_directory = r'%AppData%\Mozilla\Firefox\Profiles\nyilpyl1.adlibParsingProf'
    profile_id = "432137886"
    req_url_start = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1"
    req_url_end = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop"
    try:
        requests.get(req_url_end)
        time.sleep(5)
    except:
        pass
    response = requests.get(req_url_start)
    time.sleep(2)
    response_json = response.json()
    print(response_json)
    port = response_json['automation']['port']
    options = Options()
    options.debugger_address = f'127.0.0.1:{port}'
    driver = webdriver.Chrome(options=options)
    driver.get(url_with_filters)
    time.sleep(1)
    driver.get(url_with_filters)
    time.sleep(1)
    try:
        _ = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='_7jvw x2izyaf x1hq5gj4 x1d52u69']")))
    except TimeoutException:
        driver.refresh()
        time.sleep(1)
    account.name = driver.find_element(By.XPATH, "//div[@class='x8t9es0 x1ldc4aq x1xlr1w8 x1cgboj8 x4hq6eo xq9mrsl x1yc453h x1h4wwuj xeuugli']").text
    try:
        account.nickname = "@" + driver.find_elements(By.XPATH, "//a[@class='xt0psk2 x1hl2dhg xt0b8zv x8t9es0 x1fvot60 xxio538 xjnfcd9 xq9mrsl x1yc453h x1h4wwuj x1fcty0u']")[-1].get_attribute("href").split("/")[-1]
    except:
        account.nickname = "@"
    try:
        account.image = driver.find_element(By.XPATH, "//img[@class='xl1xv1r x78zum5 x193iq5w x1us19tq xkrh0ho x1aqa79q x10btfu9 x1e152vy']").get_attribute("src")
    except:
        account.image = "#"
    print(f"To Parse: {account.name}, {account.nickname}")
    footer = driver.find_element(By.XPATH, "//div[@class='xq4jnbd x78zum5 xdt5ytf xr1yuqi xkrivgy x4ii5y1 x1gryazu "
                                           "x1dr75xp xz9dl7a']")
    account.link = url_with_filters
    last_len = 0
    count = 0
    while True:
        # get content
        try:
            page_content = driver.find_elements(By.XPATH, "//div[@class='_7jvw x2izyaf x1hq5gj4 x1d52u69']")
        except:
            time.sleep(3)
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
    driver.quit()
    try:
        requests.get(req_url_end)
        time.sleep(5)
    except:
        pass
    print(f"End {account.name}.")
    account_id = account.id

    db_sess = db_session.create_session()
    old_ads_id = db_sess.query(Advertisements.ad_id_another).all()
    old_ads_id = [ad[0] for ad in old_ads_id]
    account_name = "_".join([i for i in account.name.split() if i.isalpha()])
    original_zip_active = download_zip_from_s3(f"{account_name}/{account_name}_active_media.zip", account_name, "Active")
    original_zip_inactive = download_zip_from_s3(f"{account_name}/{account_name}_inactive_media.zip", account_name,
                                                 "Inactive")
    additional_files_active = {}
    additional_files_inactive = {}
    account_name_image = requests.get(account.image)
    if account_name_image.status_code == 200:
        account_name_image_data = account_name_image.content
        key = f"{account_name}/{account_name}.jpg"
        bucket_obj.put_object(Key=key, Body=BytesIO(account_name_image_data))
        account.image = f"https://s3.timeweb.com/{bucket_name}/{account_name}/{account_name}.jpg"
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
            else:
                old_ad = db_sess.query(Advertisements).filter(Advertisements.ad_id_another == ad.id).first()
                old_ad.ad_daysActive = ad.duration
                db_sess.commit()
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


            try:

                response = requests.get(ad.download)
                if response.status_code == 200:
                    image_data = response.content
                    if ad.media_type == "Image":
                        if ad.status == "Active":
                            additional_files_active[f"{ad.id}.jpg"] = image_data
                        else:
                            additional_files_inactive[f"{ad.id}.jpg"] = image_data
                        key = f"{account_name}/{ad.id}.jpg"
                        api_ads.ad_downloadLink = f"https://s3.timeweb.com/" \
                                                  f"{bucket_name}/{account_name}/{ad.id}.jpg"
                        api_ads.ad_image = f"https://s3.timeweb.com/" \
                                           f"{bucket_name}/{account_name}/{ad.id}.jpg"

                    else:
                        response_avatar = requests.get(ad.image)
                        image_avatar_data = response_avatar.content
                        avatar_key = f"{account_name}/{ad.id}_avatar.jpg"
                        bucket_obj.put_object(Key=avatar_key, Body=BytesIO(image_avatar_data))
                        if ad.status == "Active":
                            additional_files_active[f"{ad.id}.mp4"] = image_data
                        else:
                            additional_files_inactive[f"{ad.id}.mp4"] = image_data
                        key = f"{account_name}/{ad.id}.mp4"
                        api_ads.ad_downloadLink = f"https://s3.timeweb.com/" \
                                                  f"{bucket_name}/{account_name}/{ad.id}.mp4"
                        api_ads.ad_image = f"https://s3.timeweb.com/" \
                                           f"{bucket_name}/{account_name}/{ad.id}_avatar.jpg"

                    bucket_obj.put_object(Key=key, Body=BytesIO(image_data))
            except:
                pass
            db_sess.add(api_ads)
    if original_zip_active is None:
        with zipfile.ZipFile(f"temporary_zips/{account_name}_active_media.zip", 'w') as zip_file:
            pass
        modify_zip(f"temporary_zips/{account_name}_active_media.zip", additional_files_active)
    else:
        modify_zip(f"temporary_zips/{account_name}_active_media.zip", additional_files_active)

    if original_zip_inactive is None:
        with zipfile.ZipFile(f"temporary_zips/{account_name}_inactive_media.zip", 'w') as zip_file:
            pass
        modify_zip(f"temporary_zips/{account_name}_inactive_media.zip", additional_files_inactive)
    else:
        modify_zip(f"temporary_zips/{account_name}_inactive_media.zip", additional_files_inactive)

    upload_zip_to_s3(f"temporary_zips/{account_name}_active_media.zip",
                     f"{account_name}/{account_name}_active_media.zip")
    upload_zip_to_s3(f"temporary_zips/{account_name}_inactive_media.zip",
                     f"{account_name}/{account_name}_inactive_media.zip")

    os.remove(f"temporary_zips/{account_name}_active_media.zip")
    os.remove(f"temporary_zips/{account_name}_inactive_media.zip")

    group = db_sess.query(ApiGroup).filter(ApiGroup.id == group_id).first()
    try:
        accounts_order = json.loads(group.accounts_order)
    except:
        accounts_order = []
    if accounts_order is None:
        accounts_order = []
    if int(account_id) not in accounts_order:
        accounts_order.append(int(account_id))
    group.accounts_order = json.dumps(accounts_order)
    db_sess.commit()
    db_sess.close()
    account.total_ads = len(db_sess.query(Advertisements).filter(Advertisements.account_id == account.id).all())
    account.active_ads = len(db_sess.query(Advertisements).filter(Advertisements.account_id == account.id,
                                                                  Advertisements.ad_status == "Active").all())
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
        print(f"group_id {group_id}")
        api_account.group_id = group_id
        db_sess.add(api_account)
        db_sess.commit()
    except IntegrityError:
        db_sess = db_session.create_session()
        record_to_update = db_sess.query(ApiAccount).filter(ApiAccount.acc_id == account.id).first()
        record_to_update.account_totalAds = account.total_ads
        record_to_update.account_activeAds = account.active_ads
        db_sess.commit()
        print(f"Account {account.name} already exists")
    db_sess.close()
    if ip:
        requests.post(f"{ip}/refresh/{group_id}")
    print(f"Account {account.name} in database, refresh page")


def cycle_parse_page():
    db_session.global_init("databases/accounts.db")
    db_sess = db_session.create_session()

    accounts_list = db_sess.query(ApiAccount.acc_id, ApiAccount.group_id, ApiAccount.adlib_account_link).all()
    db_sess.close()
    for acc in accounts_list:
        print(acc)
        parse_page(id_=acc[0], group_id=acc[1], url=acc[2])

