import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase

from flask_login import UserMixin


class Comment(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    under = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    publisher = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    publ_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    post = orm.relationship('Post')
    user = orm.relationship('User')

    def __repr__(self):
        return f'<comment> {self.id} {self.text}'
