import requests
import multiprocessing as mp
from flask import Flask, render_template, redirect, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from data import db_session

from parse_api.parse_requests import parse_page

app = Flask(__name__)
scheduler = BackgroundScheduler()
app.config['SECRET_KEY'] = "NikitinPlaxin31524011"
app.config['BACKEND_IP'] = "http://127.0.0.1:8800"


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
    scheduler.add_job(func=update_data, args=(id, platform, media, app.config.get('BACKEND_IP')), id=str(id),
                      trigger=IntervalTrigger(days=1))
    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response


def update_data(id, platform, media):
    process = mp.Process(target=parse_page, args=(id, platform, media))
    process.start()


def main():
    scheduler.start()
    app.run(port=8800)


if __name__ == '__main__':
    main()
