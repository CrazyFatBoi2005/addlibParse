import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Advertisements(SqlAlchemyBase):
    __tablename__ = 'advertisement'

    ad_id = sqlalchemy.Column(sqlalchemy.Integer,
                              primary_key=True)
    ad_id_another = sqlalchemy.Column(sqlalchemy.Integer)
    ad_date = sqlalchemy.Column(sqlalchemy.String)
    ad_text = sqlalchemy.Column(sqlalchemy.String)

    ad_buttonStatus = sqlalchemy.Column(sqlalchemy.String)

    ad_daysActive = sqlalchemy.Column(sqlalchemy.Integer)

    ad_downloadLink = sqlalchemy.Column(sqlalchemy.String)
    ad_landingLink = sqlalchemy.Column(sqlalchemy.String)

    ad_platform = sqlalchemy.Column(sqlalchemy.String)
    ad_mediaType = sqlalchemy.Column(sqlalchemy.String)
    ad_startDate = sqlalchemy.Column(sqlalchemy.String)

    ad_image = sqlalchemy.Column(sqlalchemy.String)

    account_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("accounts.acc_id"))

    account = orm.relationship("Account")
