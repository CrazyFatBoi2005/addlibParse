import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Job(SqlAlchemyBase):
    __tablename__ = 'jobqueue'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                              primary_key=True)
    account_id = sqlalchemy.Column(sqlalchemy.Integer)
    url = sqlalchemy.Column(sqlalchemy.String)
    time = sqlalchemy.Column(sqlalchemy.String)
