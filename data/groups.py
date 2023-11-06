import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = 'groups'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, unique=True)

    name = sqlalchemy.Column(sqlalchemy.String)

    accounts = orm.relationship('Account', back_populates='group')

