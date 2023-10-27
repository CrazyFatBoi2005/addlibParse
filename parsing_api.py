from data import db_session
import multiprocessing as mp
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from data.jobqueue import Job

from parse_requests import parse_page

app = Flask(__name__)
scheduler = BackgroundScheduler()
app.config['SECRET_KEY'] = "NikitinPlaxin31524011"
app.config['BACKEND_IP'] = "http://178.253.42.233:5000"


@app.route('/delete_job/<int:id>', methods=["POST"])
def delete_job(id):
    if scheduler.get_job(str(id)):
        scheduler.remove_job(job_id=str(id))
    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response


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


def restart_all_job():
    db_session.global_init("databases/accounts.db")
    db_sess = db_session.create_session()
    jobs = db_sess.query(Job).all()
    for job in jobs:
        time_split = job.time.split(":")
        trigger = CronTrigger(year="*", month="*", day="*", hour=time_split[0], minute=time_split[1], second=time_split[2])
        scheduler.add_job(func=update_data, kwargs={"id": job.account_id,
                                                    "url": job.url,
                                                    "ip": app.config.get('BACKEND_IP'),
                                                    "platform": None,
                                                    "media": None}, id=str(id), trigger=trigger)


def main():
    scheduler.start()
    restart_all_job()
    app.run(host="178.253.42.233", port=8800)


if __name__ == '__main__':
    main()
