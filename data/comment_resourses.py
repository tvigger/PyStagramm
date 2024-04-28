from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.comments import Comment
from data.reqparse import comment_parser

fields = ('id', 'under', 'publ_date', 'publisher', 'text')


def abort_if_comment_not_found(comment_id):
    session = db_session.create_session()
    comment = session.query(Comment).get(comment_id)
    if not comment:
        abort(404, message=f'Comment id:{comment_id} not found (╯°□°)╯')


class CommentResource(Resource):
    def get(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        return jsonify({'comment': comment.to_dict(only=fields)})

    def delete(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comment).all()
        return jsonify({'comments': [item.to_dict(only=fields) for item in comments]})

    def post(self):
        args = comment_parser.parse_args()
        session = db_session.create_session()
        comment = Comment(
            under=args['under'],
            publ_date=args['publ_date'],
            publisher=args['publisher'],
            text=args['text'],
        )
        session.add(comment)
        session.commit()
        return jsonify({'success': 'OK'})
