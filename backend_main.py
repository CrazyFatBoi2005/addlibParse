import asyncio

import requests
from flask import Flask, render_template, redirect, request, url_for

from data import db_session
from data.accounts import Account
from data.advertisement import Advertisements


app = Flask(__name__)
app.config['SECRET_KEY'] = "NikitinPlaxin315240"


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()
    accounts = db_sess.query(Account).all()
    return render_template("main.html", accounts=accounts)


@app.route('/ads', methods=["GET", "POST"])
def ads():
    return render_template("page.html")


@app.route('/add_new_page', methods=["POST"])
def add_new_page():
    form = request.form
    url = form.get("account-link")
    url = url.strip()
    id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&sort_data")]
    requests.post(f"http://127.0.0.1:8800/add_new_account/{id}")
    return redirect(f"/index")  # заменится всплывающим окном


@app.route('/refresh', methods=["POST"])
def refresh():
    print(123123123)
    return render_template("page.html")  # заменится всплывающим окном


def main():
    db_session.global_init("databases/accounts.db")

    app.run()


if __name__ == '__main__':
    main()
