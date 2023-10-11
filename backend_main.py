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
    accounts_count = len(accounts)
    return render_template("main.html", accounts=accounts, accounts_count=accounts_count)


@app.route('/ads/<int:account_id>', methods=["GET", "POST"])
def ads(account_id):
    db_sess = db_session.create_session()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id).all()
    return render_template("page.html", ads=ads)


@app.route('/add_new_page', methods=["POST"])
def add_new_page():
    form = request.form
    url = form.get("account-link")
    url = url.strip()
    id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&sort_data")]
    db_sess = db_session.create_session()
    acc_id = db_sess.query(Account).filter(Account.acc_id == id).first()
    if acc_id is None:
        requests.post(f"http://127.0.0.1:8800/add_new_account/{id}")
        return '', 204

    else:
        return render_template("back.html")


@app.route('/delete_page/<int:account_id>', methods=["POST"])
def delete_page(account_id):
    print(account_id)
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.acc_id == account_id).first()
    ads = db_sess.query(Advertisements).filter(Advertisements.account_id == account_id).all()
    db_sess.delete(account)
    for ad in ads:
        db_sess.delete(ad)
    db_sess.commit()
    return redirect(f"/index")


def main():
    db_session.global_init("databases/accounts.db")

    app.run()


if __name__ == '__main__':
    main()
