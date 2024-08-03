import csv
import datetime
import io
import json

import requests
from flask import Flask, render_template, redirect, request, Response, session, send_file, jsonify
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO
from sqlalchemy import desc

from data import db_session
from data.accounts import Account
from data.groups import Group
from data.advertisement import Advertisements
from data.jobqueue import Job
import boto3
from botocore.client import Config
from io import BytesIO
from requests_futures.sessions import FuturesSession

from parse_requests import cycle_parse_page

app = Flask(__name__)
session_ = FuturesSession()
app.config['SECRET_KEY'] = "NikitinPlaxin315240"
app.config['BUCKET_NAME'] = "7b3ae2a6-1e521fbf-430f-4275-aea8-858d0059469b"
app.config['API_IP'] = "http://178.253.42.233:8800"
socketio_ = SocketIO(app)
socketio_.init_app(app)
flask_scheduler = APScheduler()


s3 = boto3.resource(
        's3',
        endpoint_url='https://s3.timeweb.com',
        region_name='ru-1',
        aws_access_key_id='it27776',
        aws_secret_access_key='1cad6c15403631a01cc0bf26a5ce1524',
        config=Config(s3={'addressing_style': 'path'})
    )

bucket_name = "7b3ae2a6-1e521fbf-430f-4275-aea8-858d0059469b"
bucket_obj = s3.Bucket(bucket_name)


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
@app.route('/0', methods=["GET", "POST"])
@app.route('/index/0', methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()
    groups = db_sess.query(Group).all()
    groups_count = len(groups)

    if groups_count == 0:
        new_group = Group()
        new_group.id = 0
        new_group.name = "Default"
        db_sess.add(new_group)
        db_sess.commit()
    groups = db_sess.query(Group).all()
    if "Default" not in [i.name for i in groups]:
        return redirect(f"/{1}")
    groups = db_sess.query(Group).all()
    current_group_id = 0
    current_group = db_sess.query(Group).filter(Group.id == 0).first()
    try:
        accounts_order_list = json.loads(current_group.accounts_order)
    except TypeError:
        accounts_order_list = []
    accounts_order_dict = {value: i for i, value in enumerate(accounts_order_list)}
    accounts = db_sess.query(Account).filter(Account.group_id == current_group_id).all()
    accounts = sorted(accounts, key=lambda x: accounts_order_dict[x.acc_id])
    accounts_count = len(accounts)
    ad_status = "active"
    db_sess.close()
    return render_template("main.html", ad_status=ad_status, groups=groups, groups_count=groups_count,
                           current_group=current_group, accounts=accounts, accounts_count=accounts_count,
                           current_group_id=0)


@app.route('/<int:group_id>', methods=["GET", "POST"])
@app.route('/index/<int:group_id>', methods=["GET", "POST"])
def index_group(group_id):
    db_sess = db_session.create_session()
    groups = db_sess.query(Group).all()
    current_group = db_sess.query(Group).filter(Group.id == group_id).first()
    current_group_id = current_group.id
    groups_count = len(groups)
    try:
        accounts_order_list = json.loads(current_group.accounts_order)
    except TypeError:
        accounts_order_list = []
    accounts_order_dict = {value: i for i, value in enumerate(accounts_order_list)}
    accounts = db_sess.query(Account).filter(Account.group_id == current_group_id).all()
    accounts = sorted(accounts, key=lambda x: accounts_order_dict[x.acc_id])
    accounts_count = len(accounts)
    ad_status = "active"
    db_sess.close()
    return render_template("main.html", ad_status=ad_status, groups=groups, groups_count=groups_count, accounts=accounts,
                           accounts_count=accounts_count, current_group=current_group, current_group_id=current_group_id)


@app.route('/add_new_group', methods=["POST"])
def add_new_group():
    form = request.form
    group_name = form.get("group-name")
    db_sess = db_session.create_session()
    group_db = db_sess.query(Group).filter(Group.name == group_name).first()
    if not group_db:
        group = Group()
        if group_name == "Default":
            group.id = 0
        group.name = group_name
        db_sess.add(group)
        db_sess.commit()
        group_id = db_sess.query(Group.id).filter(Group.name == group_name).first()[0]
        db_sess.close()
        return redirect(f"/{group_id}")
    else:
        return "", 204


@app.route('/delete_group', methods=["POST"])
def delete_group():
    form = request.form
    action = form['send-delete-form']
    current_group_id = request.args.get("current_group_id")
    current_group_id = int(current_group_id)

    db_sess = db_session.create_session()

    if action == 'button-save':
        current_group_id = request.args.get("current_group_id")
        group_name = form.get("group-name")
        if group_name != "Default":
            new_group_id = db_sess.query(Group.id).filter(Group.name == group_name).first()[0]
            current_group_accounts = db_sess.query(Account).filter(Account.group_id == current_group_id).all()
            if len(current_group_accounts) != 0:
                pur_group = db_sess.query(Group).filter(Group.id == new_group_id).first()
                try:
                    pur_group_order = json.loads(pur_group.accounts_order)
                except:
                    pur_group_order = []
                if pur_group_order is None:
                    pur_group_order = []
                for acc in current_group_accounts:
                    acc.group_id = new_group_id
                    pur_group_order.append(acc.acc_id)
                pur_group.accounts_order = json.dumps(pur_group_order)
            current_group = db_sess.query(Group).filter(Group.id == current_group_id).first()
            db_sess.delete(current_group)
            db_sess.commit()
            return redirect(f"/{new_group_id}")

        else:
            new_group_id = 0
            current_group_accounts = db_sess.query(Account).filter(Account.group_id == current_group_id).all()
            if len(current_group_accounts) != 0:
                pur_group = db_sess.query(Group).filter(Group.id == new_group_id).first()
                pur_group_order = json.loads(pur_group.accounts_order)
                for acc in current_group_accounts:
                    acc.group_id = new_group_id
                    pur_group_order.append(acc.acc_id)
                pur_group.accounts_order = json.dumps(pur_group_order)
            current_group = db_sess.query(Group).filter(Group.id == current_group_id).first()
            db_sess.delete(current_group)
            db_sess.commit()
            db_sess.close()
            return redirect(f"/0")
    elif action == 'button-delete':
        current_group_accounts = db_sess.query(Account).filter(Account.group_id == current_group_id).all()
        for acc in current_group_accounts:
            account_job = db_sess.query(Job).filter(Job.account_id == acc.acc_id).first()
            db_sess.delete(account_job)
            acc_account_name = acc.account_name
            acc_account_name = "_".join([i for i in acc_account_name.split() if i.isalpha()])
            bucket_obj.objects.filter(Prefix=f"{acc_account_name}").delete()
            db_sess.delete(acc)
        current_group = db_sess.query(Group).filter(Group.id == current_group_id).first()
        db_sess.delete(current_group)
        db_sess.commit()
        db_sess.close()
        return redirect(f"/")


@app.route('/change_account_group', methods=["POST"])
def change_account_group():
    form = request.form
    account_id = form.get("accountIdField")
    account_id = int(account_id)
    group_name = form.get("group-name")
    db_sess = db_session.create_session()
    if group_name != "Default":
        new_group_id = db_sess.query(Group.id).filter(Group.name == group_name).first()[0]
    else:
        new_group_id = 0
    current_account = db_sess.query(Account).filter(Account.acc_id == account_id).first()

    if current_account.group_id != new_group_id:
        purpose_group = db_sess.query(Group).filter(Group.name == group_name).first()
        try:
            accounts_order_purpose_group = json.loads(purpose_group.accounts_order)
        except TypeError:
            accounts_order_purpose_group = []
        accounts_order_purpose_group.append(account_id)
        purpose_group.accounts_order = json.dumps(accounts_order_purpose_group)

        current_group = db_sess.query(Group).filter(Group.id == current_account.group_id).first()
        try:
            accounts_order_current_group = json.loads(current_group.accounts_order)
        except TypeError:
            accounts_order_current_group = []
        accounts_order_current_group.remove(account_id)
        current_group.accounts_order = json.dumps(accounts_order_current_group)

        current_account.group_id = new_group_id
        db_sess.commit()
        db_sess.close()
        requests.post(f"{app.config.get('API_IP')}/restarting_jobs")
    if new_group_id != 0:
        return redirect(f"/{new_group_id}")
    return redirect("/")


@app.route('/change_accounts_status', methods=["POST"])
def change_accounts_status():
    checkbox_statuses = request.get_json()
    checkbox_statuses = dict(checkbox_statuses)
    current_group_id = checkbox_statuses["currentGroupId"]
    db_sess = db_session.create_session()
    accounts = db_sess.query(Account).filter(Account.group_id == current_group_id).all()
    for account in accounts:
        account_checkbox_status = checkbox_statuses[f"checkbox-{account.acc_id}"]
        if account_checkbox_status:
            account.account_is_tracked = 1
            account_job = db_sess.query(Job).filter(Job.account_id == account.acc_id).first()
            if not account_job:
                new_job = Job()
                new_job.account_id = account.acc_id
                new_job.url = account.adlib_account_link
                new_job.time = datetime.datetime.now().strftime("%H:%M:%S")
                db_sess.add(new_job)
                db_sess.commit()
            else:
                pass
        else:
            account.account_is_tracked = 0
            try:
                account_job = db_sess.query(Job).filter(Job.account_id == account.acc_id).first()
                db_sess.delete(account_job)
            except:
                pass
    db_sess.commit()
    db_sess.close()
    requests.post(f"{app.config.get('API_IP')}/restarting_jobs")
    return ""


@app.route('/change_accounts_order', methods=["POST"])
def change_accounts_order():
    accounts_order_list = request.get_json()
    current_group_id = accounts_order_list[-1]
    accounts_order_list = [int(i.split("_")[-1]) for i in accounts_order_list[:-1]]
    accounts_order_list = json.dumps(accounts_order_list)
    db_sess = db_session.create_session()
    current_group = db_sess.query(Group).filter(Group.id == current_group_id).first()
    current_group.accounts_order = accounts_order_list
    db_sess.commit()
    db_sess.close()
    return ""


@app.route('/add_new_page', methods=["POST"])
def add_new_page():
    form = request.form
    url = form.get("account-link")
    url = url.strip()

    id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&search_type")]
    if not id.isdigit():
        id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&sort_data")]
    platforms = form.get("platform")
    media_type = form.get("media")
    group_name = form.get("group")
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.acc_id == id).first()
    if group_name != "Default":
        group_id = db_sess.query(Group.id).filter(Group.name == group_name).first()[0]
    else:
        group_id = 0
    db_sess.close()
    if account is None:
        requests.post(f"{app.config.get('API_IP')}/add_new_account/{id}/{platforms}/{media_type}/{group_id}")
        return "", 204

    else:
        socketio_.emit("show_modal", "OK:200")
        return "", 204


@app.route('/ads', methods=["GET", "POST"])
def ads():
    filtered = 0
    ad_status = "active"
    account_id = request.args.get("account_id")
    db_sess = db_session.create_session()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_status ==
                                               "Active").order_by(desc(Advertisements.ad_daysActive)).all()
    account_name, adlib_account_link = db_sess.query(Account.account_name, Account.adlib_account_link).filter(Account.acc_id == account_id).first()
    account_name_for_download = "_".join([i for i in account_name.split() if i.isalpha()])
    ads_count = len(ads)
    cur_date = str(datetime.date.today())
    group_id = db_sess.query(Account.group_id).filter(Account.acc_id == account_id).first()[0]
    db_sess.close()
    return render_template("page.html", ads=ads, ads_count=ads_count, cur_date=cur_date, account_id=account_id,
                           account_name=account_name,
                           adlib_account_link=adlib_account_link, filtered=filtered, ad_status=ad_status,
                           account_name_for_download=account_name_for_download, group_id=group_id,
                           bucket_naming=app.config.get("BUCKET_NAME"))


@app.route('/inactive_ads/', methods=["GET", "POST"])
def inactive_ads():
    ad_status = "inactive"
    account_id = request.args.get("account_id")
    db_sess = db_session.create_session()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_status == "Inactive").order_by(desc(Advertisements.ad_daysActive)).all()
    account_name, adlib_account_link = db_sess.query(Account.account_name, Account.adlib_account_link).filter(Account.acc_id == account_id).first()
    ads_count = len(ads)
    cur_date = str(datetime.date.today())
    group_id = db_sess.query(Account.group_id).filter(Account.acc_id == account_id).first()[0]
    db_sess.close()
    account_name_for_download = "_".join([i for i in account_name.split() if i.isalpha()])

    return render_template("page_inactive.html", ads=ads, ads_count=ads_count, cur_date=cur_date, account_id=account_id,
                           account_name=account_name,
                           adlib_account_link=adlib_account_link, ad_status=ad_status,
                           account_name_for_download=account_name_for_download,
                           bucket_naming=app.config.get("BUCKET_NAME"), group_id=group_id)


@app.route('/delete_page/<int:account_id>', methods=["POST"])
def delete_page(account_id):
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.acc_id == account_id).first()
    cur_group = db_sess.query(Group).filter(Group.id == account.group_id).first()
    cur_group_order = json.loads(cur_group.accounts_order)
    cur_group_order.remove(account_id)
    cur_group.accounts_order = json.dumps(cur_group_order)
    job = db_sess.query(Job).filter(Job.account_id == account_id).first()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id).all()
    db_sess.delete(account)
    db_sess.delete(job)
    for ad in ads:
        db_sess.delete(ad)
    db_sess.commit()
    db_sess.close()
    acc_account_name = account.account_name
    acc_account_name = "_".join([i for i in acc_account_name.split() if i.isalpha()])
    bucket_obj.objects.filter(Prefix=f"{acc_account_name}").delete()
    requests.post(f"{app.config.get('API_IP')}/delete_job/{account_id}")
    socketio_.emit('page_changed', account_id)
    return "", 204


def status1_filtration(db_sess, account_id, over_days):
    return_status = 1
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               ).order_by(desc(Advertisements.ad_daysActive)).all()
    return ads, return_status


def status2_filtration(db_sess, account_id, over_days, media_type):
    return_status = 2
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               Advertisements.ad_mediaType == media_type
                                               ).order_by(desc(Advertisements.ad_daysActive)).all()
    return ads, return_status


def status3_filtration(db_sess, account_id, over_days, platforms):
    return_status = 3
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               Advertisements.ad_platform.like(f'%{platforms}%')
                                               ).order_by(desc(Advertisements.ad_daysActive)).all()
    return ads, return_status


def status4_filtration(db_sess, account_id, over_days, platforms, media_type):
    return_status = 4
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id,
                                               Advertisements.ad_daysActive >= over_days,
                                               Advertisements.ad_mediaType == media_type,
                                               Advertisements.ad_platform.like(f'%{platforms}%')
                                               ).order_by(desc(Advertisements.ad_daysActive)).all()
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
    group_id = db_sess.query(Account.group_id).filter(Account.acc_id == account_id).first()[0]

    cur_date = str(datetime.date.today())
    account_name, adlib_account_link = db_sess.query(Account.account_name, Account.adlib_account_link).filter(Account.acc_id == account_id).first()
    db_sess.close()
    account_name_for_download = "_".join([i for i in account_name.split() if i.isalpha()])

    return render_template("page.html", ads=filtered_ads,
                           ads_count=ads_count, cur_date=cur_date,
                           account_id=account_id, account_name=account_name,
                           adlib_account_link=adlib_account_link, filtered=filtered, ad_status=ad_status,
                           account_name_for_download=account_name_for_download,
                           bucket_naming=app.config.get("BUCKET_NAME"), group_id=group_id)


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
    filename = "_".join([i for i in filename.split() if i.isalpha()])
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
    db_sess.close()
    return response


# @app.route('/install_media', methods=["POST"])
# def install_media():
#     account_id = request.args.get("account_id")
#     account_name = request.args.get("account_name")
#     account_name = "_".join([i for i in account_name.split() if i.isalpha()])
#     ad_status = request.args.get("ad_status")
#     print(ad_status)
#     if ad_status == "active":
#         socketio_.emit('disable_btn', "")
#     else:
#         socketio_.emit('inactive_disable_btn', "")
#     # session_.get(f"{app.config.get('API_IP')}/delete_media/{account_name}")
#     session_.get(f"{app.config.get('API_IP')}/delete_media/{account_name}?ad_status={ad_status}")
#     session_.get(f"{app.config.get('API_IP')}/install_media/{account_id}?ad_status={ad_status}")
#
#     return "", 204


@app.route('/download_media', methods=["POST"])
def download_media():
    ad_status = request.args.get("ad_status")
    if ad_status == "active":
        account_name = request.args.get("account_name") + "_active_media"
    else:
        account_name = request.args.get("account_name") + "_inactive_media"
    account_name = "_".join(account_name.split())
    return send_file(f"media_zips/{account_name}.zip", mimetype="application/zip")


# @app.route('/refresh_media/<int:account_id>', methods=["POST"])
# def refresh_media(account_id):
#     ad_status = request.args.get("ad_status")
#     if ad_status == "active":
#         socketio_.emit('media_is_ready', account_id)
#     else:
#         socketio_.emit('inactive_media_is_ready', account_id)
#     return "OK", 200


@app.route('/download_certain_media', methods=["POST"])
def download_certain_media():
    image_id = request.args.get("image_id")
    account_id = request.args.get("account_id")
    db_sess = db_session.create_session()
    ad_obj = db_sess.query(Advertisements).filter(Advertisements.ad_id_another == image_id).first()
    response = requests.get(ad_obj.ad_downloadLink)
    image_data = response.content
    db_sess.close()
    if ad_obj.ad_mediaType == "Video":
        return send_file(BytesIO(image_data), as_attachment=True, mimetype='application/octet-stream',
                         download_name=f"{image_id}.mp4")
    return send_file(BytesIO(image_data), as_attachment=True, mimetype='application/octet-stream',
                     download_name=f"{image_id}.jpg")


@app.route('/refresh/<int:group_id>', methods=["POST"])
def refresh(group_id):
    socketio_.emit('data_updated', group_id)
    return "OK", 200


@app.route('/receive_html', methods=['POST'])
def receive_html():
    received_data = request.get_json()

    response_data = {'message': 'Список успешно получен и обработан'}
    return jsonify(response_data)


def main():
    db_session.global_init("databases/accounts.db")
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=5000)
    flask_scheduler.add_job(id='Start Default Task', func=cycle_parse_page,
                            trigger='cron', hour=20, minute=2, second=0)
    flask_scheduler.start()

    socketio_.run(app, host="178.253.42.233", debug=True, allow_unsafe_werkzeug=True, use_reloader=False)


if __name__ == '__main__':
    main()
