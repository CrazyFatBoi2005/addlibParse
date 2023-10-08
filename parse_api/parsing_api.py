import requests
from flask import Flask, render_template, redirect, request, jsonify

from parse_api.db_data import db_session

from parse_api.db_data.accounts import Account
from parse_api.db_data.advertisement import Advertisements

from parse_requests import parse_page

app = Flask(__name__)
app.config['SECRET_KEY'] = "NikitinPlaxin31524011"


@app.route('/add_new_account/<int:id>', methods=["POST"])
def add_new_account(id):
    url = f"https://www.facebook.com/ads/library/?active_status=all" \
          f"&ad_type=all&country=ALL&view_all_page_id={id}" \
          f"&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=page&media_type=all "
    requests.post("http://127.0.0.1:5000/ok_status")
    parse_page(url, {})
    requests.post("http://127.0.0.1:5000/")


def main():
    db_session.global_init("db/accounts_api.db")
    app.run(port=8800)


if __name__ == '__main__':
    main()
