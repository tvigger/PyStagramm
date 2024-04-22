from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('surname')
parser.add_argument('nickname', required=True)
parser.add_argument('about')
parser.add_argument('email', required=True)
parser.add_argument('hashed_password', required=True)

