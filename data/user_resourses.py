from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.users import User
from data.posts import Post
from data.subscribes import Subscribe
from data.comments import Comment
from data.reqparse import user_parser

from config import PORT, HOST

from werkzeug.security import generate_password_hash

import shutil

from requests import delete as d


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
        posts = session.query(Post).filter(Post.owner == user.id).all()
        for p in posts:
            d(f'http://{HOST}:{PORT}/api/posts/{p.id}')
        subs = session.query(Subscribe).filter((Subscribe.follower == user_id) | (Subscribe.following == user.id)).all()
        for s in subs:
            session.delete(s)
        comments = session.query(Comment).filter(Comment.publisher == user.id).all()
        for com in comments:
            d(f'http://{HOST}:{PORT}/api/comments/{com.id}')
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