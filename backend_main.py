from flask import Flask, render_template, redirect, request

from db_data import db_session

from db_data import db_session
from db_data.accounts import Account
from db_data.advertisement import Advertisements

app = Flask(__name__)
app.config['SECRET_KEY'] = "NikitinPlaxin315240"


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    return render_template("main.html")


@app.route('/ads', methods=["GET", "POST"])
def ads():
    return render_template("page.html")


@app.route('/add_new_page', methods=["POST"])
def add_new_page():
    form = request.form
    account_link = form.get("account-link")
    return redirect(f"/index")


def main():
    db_session.global_init("db/accounts.db")
    app.run()


if __name__ == '__main__':
    main()
