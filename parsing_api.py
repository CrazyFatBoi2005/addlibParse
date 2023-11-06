import os
import shutil
import time
import zipfile
from io import BytesIO

import requests
from apscheduler.jobstores.base import ConflictingIdError

from data import db_session
import multiprocessing as mp
from flask import Flask, jsonify, send_file, request
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
    ad_status = request.args.get("ad_status")
    db_sess = db_session.create_session()
    acc_name = db_sess.query(Account.account_name).filter(Account.acc_id == account_id)[0][0]
    if ad_status == "active":
        download_links = db_sess.query(Advertisements.ad_downloadLink, Advertisements.ad_id_another,
                                       Advertisements.ad_mediaType) \
            .filter(Advertisements.account_id == account_id, Advertisements.ad_status == "Active").all()

        with zipfile.ZipFile(f"temporary_zips/{acc_name}_active_media.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_url, ad_id_another, media_type in download_links:
                try:
                    response = requests.get(image_url)

                    if response.status_code == 200:
                        image_data = response.content
                        if "Video" in media_type:
                            zipf.writestr(f'video_{ad_id_another}.mp4', image_data)
                        else:
                            zipf.writestr(f'image_{ad_id_another}.jpg', image_data)
                except:
                    continue
        print("It's done!")
        file_to_move = f"{acc_name}_active_media.zip"
        source_path = os.path.join("temporary_zips", file_to_move)
        destination_path = os.path.join("media_zips", file_to_move)
        shutil.move(source_path, destination_path)
    else:
        download_links = db_sess.query(Advertisements.ad_downloadLink, Advertisements.ad_id_another,
                                       Advertisements.ad_mediaType) \
            .filter(Advertisements.account_id == account_id, Advertisements.ad_status == "Inactive").all()

        with zipfile.ZipFile(f"temporary_zips/{acc_name}_inactive_media.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_url, ad_id_another, media_type in download_links:
                try:
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
        file_to_move = f"{acc_name}_inactive_media.zip"
        source_path = os.path.join("temporary_zips", file_to_move)
        destination_path = os.path.join("media_zips", file_to_move)
        shutil.move(source_path, destination_path)
    requests.post(f"{app.config.get('BACKEND_IP')}/refresh_media/{account_id}?ad_status={ad_status}")
    return "200"


@app.route("/delete_media/<string:account_name>", methods=["POST", "GET"])
def delete_media(account_name):
    try:
        ad_status = request.args.get("ad_status")
        if ad_status == "active":
            os.unlink(f"media_zips/{account_name}_active_media.zip")
        else:
            os.unlink(f"media_zips/{account_name}_inactive_media.zip")
    except:
        pass
    return "200"


@app.route('/check_fully_download/<string:account_name>', methods=["POST", "GET"])
def check_fully_download(account_name):
    ad_status = request.args.get("ad_status")
    if ad_status == "active":
        file_path = f"media_zips/{account_name}_active_media.zip"
        file_exists = os.path.exists(file_path)
        print(file_exists)
    else:
        file_path = f"media_zips/{account_name}_inactive_media.zip"
        file_exists = os.path.exists(file_path)
        print(file_exists)
    response = jsonify({"status": file_exists})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/add_new_account/<int:id>/<string:platform>/<string:media>/<int:group_id>', methods=["POST"])
def add_new_account(id, platform, media, group_id):
    process = mp.Process(target=parse_page, args=(id, group_id, platform, media, app.config.get('BACKEND_IP')))
    process.start()
    scheduler.add_job(func=update_data, args=(id, platform, media, app.config.get('BACKEND_IP'), None, group_id),
                      id=str(id),
                      trigger=IntervalTrigger(days=1))
    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response


@app.route('/restarting_jobs', methods=["POST"])
def restarting_jobs():
    restart_all_job()
    return "", 204


def update_data(id, platform, media, ip, url, group_id):
    process = mp.Process(target=parse_page, args=(id, platform, media, ip, url, group_id))
    process.start()


def restart_all_job():
    db_session.global_init("databases/accounts.db")
    db_sess = db_session.create_session()
    jobs = db_sess.query(Job).all()
    for job in jobs:
        time_split = job.time.split(":")
        trigger = CronTrigger(year="*", month="*", day="*", hour=time_split[0], minute=time_split[1], second=time_split[2])
        try:
            scheduler.add_job(func=update_data, kwargs={"id": job.account_id,
                                                        "url": job.url,
                                                        "ip": app.config.get('BACKEND_IP'),
                                                        "platform": None,
                                                        "media": None,
                                                        "group_id": None}, id=str(job.account_id), trigger=trigger)
        except ConflictingIdError:
            scheduler.resume_job(str(job.account_id))


def main():
    db_session.global_init("databases/accounts.db")
    scheduler.start()
    restart_all_job()
    print("job_rest")
    app.run(host="127.0.0.1", port=8800, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
