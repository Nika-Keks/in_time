import datetime

from flask import request
from flask_login import current_user
from flask_restx import Resource, reqparse
from flask_restx.inputs import time

from app import api
from app.models.restaurant import Restaurant
from app.utils.exceptions import ITPUpdateError, ITPForbiddenError


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


@api.route('/restaurants/<int:rest_id>')
class RestaurantById(Resource):
    def get(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        return Restaurant.query.filter_by(id=rest_id).first_or_404()

    @api.expect(update_args)
    def put(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous or\
                Restaurant.query.filter_by(user_id=current_user.id).first() is None:
            raise ITPForbiddenError()

        restaurant = Restaurant.query.filter_by(user_id=current_user.id, id=rest_id).first_or_404()
        try:
            restaurant.validate_update(**request.args)
        except ValueError:
            raise ITPUpdateError()

        restaurant.update(**request.args)
        return restaurant


# TODO: add filtering
@api.route('/restaurants/')
class Restaurants(Resource):
    def get(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        return Restaurant.query.all()
