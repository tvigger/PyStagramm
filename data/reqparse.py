from flask_restful import reqparse

post_parser = reqparse.RequestParser()
post_parser.add_argument('owner', required=True)
post_parser.add_argument('publ_date', required=True)
post_parser.add_argument('img_amount', required=True)
post_parser.add_argument('title', required=True)
post_parser.add_argument('text', required=True)

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', required=True)
user_parser.add_argument('surname')
user_parser.add_argument('nickname', required=True)
user_parser.add_argument('about')
user_parser.add_argument('email', required=True)
user_parser.add_argument('hashed_password', required=True)

comment_parser = reqparse.RequestParser()
comment_parser.add_argument('under', required=True)
comment_parser.add_argument('publ_date', required=True)
comment_parser.add_argument('publisher', required=True)
comment_parser.add_argument('text', required=True)