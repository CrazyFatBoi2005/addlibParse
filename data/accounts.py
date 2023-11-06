import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Account(SqlAlchemyBase):
    __tablename__ = 'accounts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, unique=True)

    acc_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)

    adlib_account_link = sqlalchemy.Column(sqlalchemy.String)

    account_name = sqlalchemy.Column(sqlalchemy.String)
    account_username = sqlalchemy.Column(sqlalchemy.String)

    account_totalAds = sqlalchemy.Column(sqlalchemy.Integer)

    account_activeAds = sqlalchemy.Column(sqlalchemy.Integer)

    account_socialMedia_link = sqlalchemy.Column(sqlalchemy.String)

    account_image = sqlalchemy.Column(sqlalchemy.String)

    account_is_tracked = sqlalchemy.Column(sqlalchemy.Integer, default=1)

    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'))

    group = orm.relationship('Group', back_populates='accounts')
    ads = orm.relationship("Advertisements", back_populates="account")
