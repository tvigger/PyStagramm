import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase

from flask_login import UserMixin


class Subscribe(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'subscribes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    follower = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    following = sqlalchemy.Column(sqlalchemy.Integer)
    who = orm.relationship('User')
    targ = orm.relationship('User')
