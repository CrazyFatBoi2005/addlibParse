import asyncio
import csv
import datetime
import io
import os

import requests
import socketio
from flask import Flask, render_template, redirect, request, url_for, Response, session, send_file
from flask_socketio import SocketIO

from data import db_session
from data.accounts import Account
from data.advertisement import Advertisements
from data.jobqueue import Job

from io import BytesIO
import zipfile
from requests_futures.sessions import FuturesSession

app = Flask(__name__)
session_ = FuturesSession()
app.config['SECRET_KEY'] = "NikitinPlaxin315240"
app.config['API_IP'] = "http://127.0.0.1:8800"
socketio = SocketIO(app)


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()
    accounts = db_sess.query(Account).all()
    accounts_count = len(accounts)
    ad_status = "active"
    return render_template("main.html", accounts=accounts, accounts_count=accounts_count, ad_status=ad_status)


@app.route('/ads', methods=["GET", "POST"])
def ads():
    filtered = 0
    ad_status = "active"
    account_id = request.args.get("account_id")
    db_sess = db_session.create_session()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_status == "Active").all()
    account_name, adlib_account_link = db_sess.query(Account.account_name, Account.adlib_account_link).filter(Account.acc_id == account_id).first()
    ads_count = len(ads)
    cur_date = str(datetime.date.today())
    return render_template("page.html", ads=ads, ads_count=ads_count, cur_date=cur_date, account_id=account_id,
                           account_name=account_name,
                           adlib_account_link=adlib_account_link, filtered=filtered, ad_status=ad_status)


@app.route('/inactive_ads/', methods=["GET", "POST"])
def inactive_ads():
    ad_status = "inactive"
    account_id = request.args.get("account_id")
    db_sess = db_session.create_session()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_status == "Inactive").all()
    account_name, adlib_account_link = db_sess.query(Account.account_name, Account.adlib_account_link).filter(Account.acc_id == account_id).first()
    ads_count = len(ads)
    cur_date = str(datetime.date.today())
    return render_template("page_inactive.html", ads=ads, ads_count=ads_count, cur_date=cur_date, account_id=account_id,
                           account_name=account_name,
                           adlib_account_link=adlib_account_link, ad_status=ad_status)


@app.route('/add_new_page', methods=["POST"])
def add_new_page():
    form = request.form
    url = form.get("account-link")
    url = url.strip()

    id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&search_type")]
    if not id.isdigit():
        id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&sort_data")]
    print(id)
    platforms = form.get("platform")
    media_type = form.get("media")
    db_sess = db_session.create_session()
    acc_id = db_sess.query(Account).filter(Account.acc_id == id).first()
    if acc_id is None:
        requests.post(f"{app.config.get('API_IP')}/add_new_account/{id}/{platforms}/{media_type}")
        return "", 204

    else:
        socketio.emit("show_modal", "OK:200")
        return "", 204


@app.route('/delete_page/<int:account_id>', methods=["POST"])
def delete_page(account_id):
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.acc_id == account_id).first()
    job = db_sess.query(Job).filter(Job.account_id == account_id).first()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id).all()
    db_sess.delete(account)
    db_sess.delete(job)
    for ad in ads:
        db_sess.delete(ad)
    db_sess.commit()

    requests.post(f"{app.config.get('API_IP')}/delete_job/{account_id}")
    return redirect(f"/index")


def status1_filtration(db_sess, account_id, over_days):
    return_status = 1
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               ).all()
    return ads, return_status


def status2_filtration(db_sess, account_id, over_days, media_type):
    return_status = 2
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               Advertisements.ad_mediaType == media_type
                                               ).all()
    return ads, return_status


def status3_filtration(db_sess, account_id, over_days, platforms):
    return_status = 3
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               Advertisements.ad_platform.like(f'%{platforms}%')
                                               ).all()
    return ads, return_status


def status4_filtration(db_sess, account_id, over_days, platforms, media_type):
    return_status = 4
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               Advertisements.ad_mediaType == media_type,
                                               Advertisements.ad_platform.like(f'%{platforms}%')
                                               ).all()
    return ads, return_status


def text_filter(text, ad_text):
    if text.strip().lower() in ad_text.lower():
        return True
    return False


@app.route('/filter_ads', methods=["POST"])
def filter_ads():
    filtered = 1
    account_id = request.args.get("account_id")
    ad_status = request.args.get("ad_status")
    request_data = request.form
    text, over_days, platforms, media_type, start_date = request_data.get("contains-text"), \
                                                         request_data.get("over"), \
                                                         request_data.get("platforms"), \
                                                         request_data.get("media"), \
                                                         request_data.get("start-date")
    db_sess = db_session.create_session()
    if media_type == "All Types" and platforms == "All Platforms":
        ads, return_status = status1_filtration(db_sess, account_id, over_days)
    elif media_type != "All Types" and platforms == "All Platforms":
        ads, return_status = status2_filtration(db_sess, account_id, over_days, media_type)
    elif media_type == "All Types" and platforms != "All Platforms":
        ads, return_status = status3_filtration(db_sess, account_id, over_days, platforms)
    elif media_type != "All Types" and platforms != "All Platforms":
        ads, return_status = status4_filtration(db_sess, account_id, over_days, platforms, media_type)
    filtered_ads = []
    for ad in ads:
        if datetime.datetime.strptime(start_date, '%Y-%m-%d').date() != datetime.date.today():
            if datetime.datetime.strptime(ad.start_date,
                                          '%Y-%m-%d').date() >= datetime.datetime.strptime(start_date,
                                                                                           '%Y-%m-%d').date():
                if text_filter(text, ad.ad_text):
                    filtered_ads.append(ad)
        else:
            if text_filter(text, ad.ad_text):
                filtered_ads.append(ad)
    if ad_status == "active":
        filtered_ads = [ad for ad in filtered_ads if ad.ad_status == "Active"]
    else:
        filtered_ads = [ad for ad in filtered_ads if ad.ad_status == "Inactive"]
    filtered_id = [i.ad_id_another for i in filtered_ads]
    session["sorted_ids"] = filtered_id
    ads_count = len(filtered_ads)

    cur_date = str(datetime.date.today())
    account_name, adlib_account_link = db_sess.query(Account.account_name, Account.adlib_account_link).filter(Account.acc_id == account_id).first()

    return render_template("page.html", ads=filtered_ads,
                           ads_count=ads_count, cur_date=cur_date,
                           account_id=account_id, account_name=account_name,
                           adlib_account_link=adlib_account_link, filtered=filtered, ad_status=ad_status)


@app.route('/download_csv', methods=["POST", "GET"])
def download_csv():
    sorted_ids = session.get('sorted_ids', [])
    filtered = request.args.get("filtered")
    account_id = request.args.get("account_id")
    ad_status = request.args.get("ad_status")
    db_sess = db_session.create_session()
    if filtered == "1":
        ads = []
        for sorted_id in sorted_ids:
            ads.append(db_sess.query(Advertisements).filter(Advertisements.ad_id_another == sorted_id).first())
    else:
        if ad_status == "active":
            ads = db_sess.query(Advertisements).filter(Advertisements.ad_status == "Active",
                                                       Advertisements.account_id == account_id).all()
        else:
            ads = db_sess.query(Advertisements).filter(Advertisements.ad_status == "Inactive",
                                                       Advertisements.account_id == account_id).all()
    filename = db_sess.query(Account.account_name).filter(Account.acc_id == account_id).first()[0]
    filename = "_".join(filename.split())
    csv_names_structure = ["ad_id", "ad_accountId", "start_date", "end_date", "ad_text",
                           "ad_buttonStatus", "ad_daysActive", "ad_downloadLink",
                           "ad_landingLink", "ad_platform", "ad_image"]

    data = [csv_names_structure]
    for ad in ads:
        ad_id, ad_accountId, ad_start_date, ad_end_date, \
        ad_text, ad_buttonStatus, \
        ad_daysActive, \
        ad_downloadLink, \
        ad_landingLink, \
        ad_platform, \
        ad_image = ad.ad_id_another, ad.account_id, ad.ad_start_date, ad.ad_end_date, \
                   ad.ad_text, ad.ad_buttonStatus, ad.ad_daysActive, \
                   ad.ad_downloadLink, ad.ad_landingLink, ad.ad_platform, ad.ad_image
        data.append([ad_id, ad_accountId, ad_start_date, ad_end_date, ad_text, ad_buttonStatus,
                     ad_daysActive, ad_downloadLink, ad_landingLink, ad_platform, ad_image])

    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerows(data)
    csv_data = csv_buffer.getvalue()
    csv_buffer.close()
    content_type = 'text/csv'
    response = Response(csv_data, content_type=content_type)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    return response


# def my_callback_function(resp, *args, **kwargs):
#     print(123, 123, 123, "\n")
#     socketio.emit('media_is_ready', "OK:200")
#     return "OK", 200


@app.route('/install_media', methods=["POST"])
def install_media():
    account_id = request.args.get("account_id")
    account_name = request.args.get("account_name")
    ad_status = request.args.get("ad_status")
    print(ad_status)
    if ad_status == "active":
        socketio.emit('disable_btn', "")
    else:
        socketio.emit('inactive_disable_btn', "")
    # session_.get(f"{app.config.get('API_IP')}/delete_media/{account_name}")
    session_.get(f"{app.config.get('API_IP')}/delete_media/{account_name}?ad_status={ad_status}")
    session_.get(f"{app.config.get('API_IP')}/install_media/{account_id}?ad_status={ad_status}")

    return "", 204


@app.route('/download_media', methods=["POST"])
def download_media():
    ad_status = request.args.get("ad_status")
    if ad_status == "active":
        account_name = request.args.get("account_name") + "_active_media"
    else:
        account_name = request.args.get("account_name") + "_inactive_media"

    return send_file(f"media_zips/{account_name}.zip", mimetype="application/zip")


@app.route('/refresh_media/<int:account_id>', methods=["POST"])
def refresh_media(account_id):
    ad_status = request.args.get("ad_status")
    if ad_status == "active":
        socketio.emit('media_is_ready', account_id)
    else:
        socketio.emit('inactive_media_is_ready', account_id)
    return "OK", 200


@app.route('/download_certain_media', methods=["POST"])
def download_certain_media():
    image_id = request.args.get("image_id")
    db_sess = db_session.create_session()
    image_download_link, image_media_type = \
        db_sess.query(Advertisements.ad_downloadLink,
                      Advertisements.ad_mediaType).filter(Advertisements.ad_id_another == image_id)[0]

    response = requests.get(image_download_link)

    if response.status_code == 200:
        image_data = response.content
        if image_media_type == "Image":
            return send_file(
                BytesIO(image_data),
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=f'{image_id}.jpg'
            )
        return send_file(
            BytesIO(image_data),
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'{image_id}.mp4'
        )


@app.route('/refresh', methods=["POST"])
def refresh():
    socketio.emit('data_updated', "OK:200")
    return "OK", 200


def main():
    db_session.global_init("databases/accounts.db")

    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
