from flask_restful import reqparse

post_parser = reqparse.RequestParser()
post_parser.add_argument('owner', required=True)
post_parser.add_argument('publ_date', required=True)
post_parser.add_argument('likes', required=True)
post_parser.add_argument('title', required=True)
post_parser.add_argument('text', required=True)