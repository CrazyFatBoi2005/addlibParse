import requests
import multiprocessing as mp
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

    process = mp.Process(target=parse_page, args=(url, {}))
    process.start()
    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response


def main():
    db_session.global_init("db/accounts_api.db")
    app.run(port=8800)


if __name__ == '__main__':
    main()
