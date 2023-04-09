from flask import request
from flask_login import current_user
from flask_restx import Resource

from app import api
from app.models.user import User
from app.utils.exceptions import ITPForbiddenError, ITPUpdateError


@api.route('/user/<int:user_id>')
class User(Resource):
    def get(self, user_id):
        if not current_user.is_authenticated or current_user.is_anonymous or current_user.id != user_id:
            raise ITPForbiddenError()
        user = User.query.filter_by(id=user_id).first_or_404()
        return user

    @api.param('name', type=str, help='New user name')
    @api.param('email', type=str, help='New user email')
    @api.param('password', type=str, help='New user password')
    def put(self, user_id):
        if not current_user.is_authenticated or current_user.is_anonymous or current_user.id != user_id:
            ITPForbiddenError()
        user = User.query.filter_by(id=user_id).first_or_404()
        try:
            user.validate_update(**request.args)
        except ValueError:
            raise ITPUpdateError()

        user.update(**request.args)
        return user
