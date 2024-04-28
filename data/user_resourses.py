from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.users import User
from data.posts import Post
from data.comments import Comment
from data.reqparse import user_parser

from werkzeug.security import generate_password_hash

import shutil

def set_password(password):
    return generate_password_hash(password)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('name', 'surname', 'nickname', 'about', 'email', 'hashed_password'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        posts = session.query(Post).filter(Post.owner == user.id)
        for p in posts:
            comms = session.query(Comment).filter(Comment.under == p.id)
            for c in comms:
                session.delete(c)
            session.delete(p)
        shutil.rmtree(f'static/img/users_images/{user.id}')
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'surname', 'nickname', 'about', 'email', 'hashed_password')) for item in users]})

    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        users = User(
            name=args['name'],
            surname=args['surname'],
            nickname=args['nickname'],
            about=args['about'],
            email=args['email'],
            hashed_password=set_password(args['hashed_password'])
        )
        session.add(users)
        session.commit()
        return jsonify({'success': 'OK'})