from flask import request
from flask_login import current_user
from flask_restx import Resource

from app import api
from app.models.user import User as UserModel
from app.utils.exceptions import ITPForbiddenError, ITPInvalidError, ok


ns = api.namespace('User', description='Operations with current user')


@ns.route('/user/<int:user_id>')
class User(Resource):
    def get(self, user_id):
        if not current_user.is_authenticated or current_user.is_anonymous or current_user.id != user_id:
            raise ITPForbiddenError()
        user = UserModel.query.filter_by(id=user_id).first_or_404(f"User with id {user_id} was not found")
        return user.to_dict(), ok

    @ns.param('name', type=str, help='New user name')
    @ns.param('email', type=str, help='New user email')
    @ns.param('password', type=str, help='New user password')
    def put(self, user_id):
        if not current_user.is_authenticated or current_user.is_anonymous or current_user.id != user_id:
            ITPForbiddenError()
        user = UserModel.query.filter_by(id=user_id).first_or_404(f"User with id {user_id} was not found")
        try:
            UserModel.validate_update(**request.args)
        except ValueError:
            raise ITPInvalidError()

        UserModel.update(user_id, **request.args)
        return user.to_dict(), ok
