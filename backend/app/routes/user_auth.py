from flask import request
from flask_login import current_user, login_user, logout_user
from flask_restx import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, api
from app.models.user import User
from app.utils.exceptions import ITPAuthError


@api.route('/login')
@api.param('email', type=str, help='User email address', required=True)
@api.param('password', type=str, help='User password', required=True)
class Login(Resource):
    def post(self):
        if current_user.is_authenticated:
            return
        email = request.args.get('email')
        password = request.args.get('password')
        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.password, password):
            raise ITPAuthError(f"Wrong credentials")
        login_user(user, remember=True)


@api.route('/signup')
@api.param('name', type=str, help='User name')
@api.param('email', type=str, help='User email address', required=True)
@api.param('password', type=str, help='User password', required=True)
class Signup(Resource):
    def post(self):
        if current_user.is_authenticated:
            return
        email = request.args.get('email')
        name = request.args.get('name')
        password = request.args.get('password')

        if User.query.filter_by(email=email).first() is not None:
            raise ITPAuthError(f"User with email {email} already exists")

        if not name:
            name = email

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()


@api.route('/logout')
class Logout(Resource):
    def post(self):
        logout_user()
