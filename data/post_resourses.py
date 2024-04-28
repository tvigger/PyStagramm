from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.posts import Post
from data.comments import Comment
from data.reqparse import post_parser

from config import PORT, HOST

import shutil

from requests import delete as d

fields = ('id', 'owner', 'publ_date', 'title', 'text')


def abort_if_post_not_found(post_id):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    if not post:
        abort(404, message=f'Job id:{post_id} not found (╯°□°)╯')


class PostResource(Resource):
    def get(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        return jsonify({'post': post.to_dict(only=fields)})

    def delete(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Post).get(post_id)
        comments = session.query(Comment).filter(Comment.under == post.id).all()
        for com in comments:
            d(f'http://{HOST}:{PORT}/api/comments/{com.id}')
        shutil.rmtree(f'static/img/posts_images/{post.id}')
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


class PostsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        posts = session.query(Post).all()
        return jsonify({'posts': [item.to_dict(only=fields) for item in posts]})

    def post(self):
        args = post_parser.parse_args()
        session = db_session.create_session()
        post = Post(
            owner=args['owner'],
            publ_date=args['publ_date'],
            title=args['title'],
            text=args['text'],
        )
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})
