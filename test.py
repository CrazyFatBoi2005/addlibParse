from data import db_session
from data.accounts import Account as ApiAccount

db_session.global_init("databases/accounts.db")
db_sess = db_session.create_session()


accounts_list = db_sess.query(ApiAccount.acc_id, ApiAccount.group_id, ApiAccount.adlib_account_link).all()

print(accounts_list)