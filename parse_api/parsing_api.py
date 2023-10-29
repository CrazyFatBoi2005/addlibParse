import os
import shutil
import time
import zipfile
from io import BytesIO

import requests

from data import db_session
import multiprocessing as mp
from flask import Flask, jsonify, send_file
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from data.jobqueue import Job
from data.accounts import Account
from data.advertisement import Advertisements
from flask_cors import CORS

from parse_requests import parse_page

app = Flask(__name__)
CORS(app)
scheduler = BackgroundScheduler()
app.config['SECRET_KEY'] = "NikitinPlaxin31524011"
app.config['BACKEND_IP'] = "http://127.0.0.1:5000"


@app.route('/delete_job/<int:id>', methods=["POST"])
def delete_job(id):
    if scheduler.get_job(str(id)):
        scheduler.remove_job(job_id=str(id))
    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response


@app.route('/install_media/<int:account_id>', methods=["POST", "GET"])
def install_media(account_id):
    print("It's started")
    db_sess = db_session.create_session()
    acc_name = db_sess.query(Account.account_name).filter(Account.acc_id == account_id)[0][0]
    download_links = db_sess.query(Advertisements.ad_downloadLink, Advertisements.ad_id_another,
                                   Advertisements.ad_mediaType) \
        .filter(Advertisements.account_id == account_id).all()

    with zipfile.ZipFile(f"../temporary_zips/{acc_name}_media.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for image_url, ad_id_another, media_type in download_links:
            try:
                # proxies = {
                #     'http': f'http://aAnD9etY:5iYLwNwe@46.3.24.210:64358',
                #     'https': f'http://aAnD9etY:5iYLwNwe@46.3.24.210:64358',
                # }
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = response.content
                    if "Video" in media_type:
                        zipf.writestr(f'video_{ad_id_another}.mp4', image_data)
                    else:
                        zipf.writestr(f'image_{ad_id_another}.jpg', image_data)
            except requests.exceptions.MissingSchema:
                continue
    print("It's done!")
    file_to_move = f"{acc_name}_media.zip"
    source_path = os.path.join("../temporary_zips", file_to_move)
    destination_path = os.path.join("../media_zips", file_to_move)
    shutil.move(source_path, destination_path)
    requests.post(f"{app.config.get('BACKEND_IP')}/refresh_media/{account_id}")
    return "200"


@app.route('/check_fully_download/<string:account_name>', methods=["POST", "GET"])
def check_fully_download(account_name):
    file_path = f"../media_zips/{account_name}_media.zip"
    file_exists = os.path.exists(file_path)
    print(file_exists)
    return jsonify({"status": file_exists})


@app.route('/add_new_account/<int:id>/<string:platform>/<string:media>', methods=["POST"])
def add_new_account(id, platform, media):
    process = mp.Process(target=parse_page, args=(id, platform, media, app.config.get('BACKEND_IP')))
    process.start()
    scheduler.add_job(func=update_data, args=(id, platform, media, app.config.get('BACKEND_IP'), None), id=str(id),
                      trigger=IntervalTrigger(days=1))
    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response


def update_data(id, platform, media, ip, url):
    process = mp.Process(target=parse_page, args=(id, platform, media, ip, url))
    process.start()


# def restart_all_job():
#     db_session.global_init("../databases/accounts.db")
#     db_sess = db_session.create_session()
#     jobs = db_sess.query(Job).all()
#     for job in jobs:
#         time_split = job.time.split(":")
#         trigger = CronTrigger(year="*", month="*", day="*", hour=time_split[0], minute=time_split[1], second=time_split[2])
#         scheduler.add_job(func=update_data, kwargs={"id": job.account_id,
#                                                     "url": job.url,
#                                                     "ip": app.config.get('BACKEND_IP'),
#                                                     "platform": None,
#                                                     "media": None}, id=str(id), trigger=trigger)


def main():
    scheduler.start()
    # restart_all_job()
    db_session.global_init("../databases/accounts.db")
    app.run(host="127.0.0.1", port=8800, debug=True)


if __name__ == '__main__':
    main()
