import threading

import requests
import multiprocessing as mp
from flask import Flask, render_template, redirect, request, jsonify

from data import db_session


from parse_api.parse_requests import parse_page

app = Flask(__name__)
app.config['SECRET_KEY'] = "NikitinPlaxin31524011"


@app.route('/add_new_account/<int:id>/<string:platform>/<string:media>', methods=["POST"])
def add_new_account(id, platform, media):
    process = mp.Process(target=parse_page, args=(id, platform, media))
    process.start()

    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response


def main():

    app.run(port=8800)


if __name__ == '__main__':
    main()
