import asyncio
import datetime

import requests
import socketio
from flask import Flask, render_template, redirect, request, url_for
from flask_socketio import SocketIO

from data import db_session
from data.accounts import Account
from data.advertisement import Advertisements

app = Flask(__name__)
app.config['SECRET_KEY'] = "NikitinPlaxin315240"
socketio = SocketIO(app)


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()
    accounts = db_sess.query(Account).all()
    accounts_count = len(accounts)
    return render_template("main.html", accounts=accounts, accounts_count=accounts_count)


@app.route('/ads/<int:account_id>', methods=["GET", "POST"])
def ads(account_id):
    db_sess = db_session.create_session()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id).all()
    ads_count = len(ads)
    cur_date = str(datetime.date.today())
    print(cur_date)
    return render_template("page.html", ads=ads, ads_count=ads_count, cur_date=cur_date, account_id=account_id)


@app.route('/add_new_page', methods=["POST"])
def add_new_page():
    form = request.form
    url = form.get("account-link")
    url = url.strip()
    id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&sort_data")]
    platforms = form.get("platform")
    media_type = form.get("media")
    db_sess = db_session.create_session()
    acc_id = db_sess.query(Account).filter(Account.acc_id == id).first()
    print(f"http://127.0.0.1:8800/add_new_account/{id}/{platforms}/{media_type}")
    if acc_id is None:
        requests.post(f"http://127.0.0.1:8800/add_new_account/{id}/{platforms}/{media_type}")
        return "", 204

    else:
        socketio.emit("show_modal", "OK:200")
        return "", 204


@app.route('/delete_page/<int:account_id>', methods=["POST"])
def delete_page(account_id):
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.acc_id == account_id).first()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id).all()
    db_sess.delete(account)
    for ad in ads:
        db_sess.delete(ad)
    db_sess.commit()

    requests.post(f"http://127.0.0.1:8800/delete_job/{account_id}")
    return redirect(f"/index")


@app.route('/filter_ads', methods=["POST"])
def filter_ads():
    account_id = request.args.get("account_id")
    request_data = request.form
    text, over_days, platforms, media_type, start_date = request_data.get("contains-text"), \
                                                         request_data.get("over"), \
                                                         request_data.get("platforms"), \
                                                         request_data.get("media"), \
                                                         request_data.get("start-date")
    db_sess = db_session.create_session()
    if media_type == "All Types" and platforms == "All Platforms":
        ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                                   Advertisements.ad_daysActive >= over_days,
                                                   ).all()
    elif media_type != "All Types" and platforms == "All Platforms":
        ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                                   Advertisements.ad_daysActive >= over_days,
                                                   Advertisements.ad_mediaType == media_type
                                                   ).all()
    elif media_type == "All Types" and platforms != "All Platforms":
        ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                                   Advertisements.ad_daysActive >= over_days,
                                                   Advertisements.ad_platform.like(f'%{platforms}%')
                                                   ).all()
    elif media_type != "All Types" and platforms != "All Platforms":
        ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                                   Advertisements.ad_daysActive >= over_days,
                                                   Advertisements.ad_mediaType == media_type,
                                                   Advertisements.ad_platform.like(f'%{platforms}%')
                                                   ).all()
    filtered_ads = []
    for ad in ads:
        if datetime.datetime.strptime(ad.ad_date, '%Y-%m-%d').date() > datetime.datetime.strptime(start_date, '%Y-%m-%d').date():
            filtered_ads.append(ad)
        #

    ads_count = len(filtered_ads)

    cur_date = str(datetime.date.today())
    return render_template("page.html", ads=filtered_ads, ads_count=ads_count, cur_date=cur_date, account_id=account_id)


@app.route('/refresh', methods=["POST"])
def refresh():
    socketio.emit('data_updated', "OK:200")
    return "OK", 200


def main():
    db_session.global_init("databases/accounts.db")

    socketio.run(app, debug=True)


if __name__ == '__main__':
    main()
