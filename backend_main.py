from flask import Flask, render_template

from db_data import db_session

from db_data import db_session
from db_data.accounts import Account
from db_data.advertisement import Advertisements

app = Flask(__name__)
app.config['SECRET_KEY'] = "NikitinPlaxin315240"


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("main.html")


@app.route('/', methods=["POST"])
def add_new_account():
    return render_template("main.html")


@app.route('/ads', methods=["GET", "POST"])
def ads():
    return render_template("page.html")


def main():
    db_session.global_init("db/accounts.db")
    app.run()


if __name__ == '__main__':
    main()
