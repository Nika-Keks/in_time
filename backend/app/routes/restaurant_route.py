import datetime

from flask import request
from flask_login import current_user
from flask_restx import Resource, reqparse
from flask_restx.inputs import time

from app import api
from app.models.restaurant import Restaurant
from app.routes.utils import pagination_args, get_pagination_args
from app.utils.exceptions import ITPInvalidError, ITPForbiddenError, ok

ns = api.namespace('Restaurant', description='Operations with existed restaurants')

get_args = pagination_args.copy()

update_args = reqparse.RequestParser()
default_open = datetime.time(9, 0, 0).isoformat()
default_close = datetime.time(18, 0, 0).isoformat()
update_args.add_argument('phone', type=str, help='New restaurant phone')
update_args.add_argument('description', type=str, help='New restaurant description')
update_args.add_argument('position', type=str, help='New restaurant position')
update_args.add_argument('wday_opening', type=time, help='New restaurant working day opening time',
                         default=default_open)
update_args.add_argument('wday_closing', type=time, help='New restaurant working day closing time',
                         default=default_close)
update_args.add_argument('wend_opening', type=time, help='New restaurant weekend opening time',
                         default=default_open)
update_args.add_argument('wend_closing', type=time, help='New restaurant weekend closing time',
                         default=default_close)


@ns.route('/restaurants/<int:rest_id>')
class RestaurantById(Resource):
    def get(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        return Restaurant.query.filter_by(id=rest_id).first_or_404(
            f"Restaurant with id {rest_id} was not found").to_dict(), ok

    @ns.expect(update_args)
    def put(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous or\
                Restaurant.query.filter_by(user_id=current_user.id).first() is None:
            raise ITPForbiddenError()

        restaurant = Restaurant.query.filter_by(user_id=current_user.id, id=rest_id).first_or_404(
            f"Restaurant with id {rest_id} for user {current_user.id} was not found")
        try:
            Restaurant.validate_update(rest_id, **request.args)
        except ValueError:
            raise ITPInvalidError()

        Restaurant.update(rest_id, **request.args)
        return restaurant.to_dict(), ok


# TODO: add filtering
@ns.route('/restaurants/')
class Restaurants(Resource):
    @ns.expect(get_args)
    def get(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        page, per_page = get_pagination_args(request.args)

        data = Restaurant.query.paginate(page=page, max_per_page=per_page, error_out=False).items
        return {"count": len(data), "items": [d.to_dict() for d in data]}, ok
