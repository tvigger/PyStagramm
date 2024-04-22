import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase

from flask_login import UserMixin


class Post(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'posts'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    publ_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    img_amount = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relationship('User')
    comment = orm.relationship('Comment', back_populates='post')

    def __repr__(self):
        return f'<post> {self.id} {self.title}'
