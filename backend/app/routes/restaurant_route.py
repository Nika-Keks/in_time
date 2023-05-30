import datetime

from flask import request
from flask_login import current_user
from flask_restx import Resource, reqparse
from flask_restx.inputs import time

from app import api, db, flask_app
from app.models.restaurant import Restaurant
from app.routes.utils import pagination_args, get_pagination_args, filter_args, get_filter_order_query
from app.utils.exceptions import ITPInvalidError, ITPForbiddenError, ITPNotFound, ok
from app.models.user import User


ns = api.namespace('Restaurant', description='Operations with existed restaurants')

get_args = pagination_args.copy()
for arg in filter_args.args:
    get_args.add_argument(arg)

search_args = pagination_args.copy()
search_args.add_argument('search_string', type=str, help='String to find by full-text search', required=True)


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


add_args = update_args.copy()
add_args.add_argument('user_id', type=int, help="Restaurant owner's ID", required=True)
add_args.replace_argument('phone', type=str, help="New restaurant owner's phone", required=True)
add_args.replace_argument('description', type=str, help='New restaurant description', required=True)
add_args.replace_argument('position', type=str, help='New restaurant position', required=True)


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


# @ns.param('description', type=str, help='Description', required=True)
# @ns.param('user_id', type=int, help='User ID', required=True)
# @ns.param('position', type=str, help='position', required=True)
# @ns.param('phone', type=str, help="Restaurant owner's phone", required=True)
# @ns.param('wday_opening', type=time, help='New restaurant working day opening time',
#           default=default_open)
# @ns.param('wday_closing', type=time, help='New restaurant working day closing time',
#           default=default_close)

@ns.route('/restaurants/add_new')
class RestaurantAdd(Resource):
    @ns.expect(add_args)
    def post(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()
        if current_user.email != "super_admin@gmail.com":
            raise ITPForbiddenError("You must be a super admin to perform this action!")
        user_id = request.args.get('user_id')
        if User.query.filter_by(id=user_id).first() is None:
            raise ITPNotFound(f"Restaurant owner with id='{user_id}' is not exist")

        new_restaurant = Restaurant(user_id=user_id,
                                    position=request.args.get('position'),
                                    description=request.args.get('description'),
                                    phone=request.args.get('phone'),
                                    wday_opening=request.args.get('wday_opening'),
                                    wday_closing=request.args.get('wday_closing'))
        db.session.add(new_restaurant)
        db.session.commit()


@ns.route('/restaurants/')
class Restaurants(Resource):
    @ns.expect(get_args)
    def get(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        page, per_page = get_pagination_args(request.args)
        query = get_filter_order_query(request.args, Restaurant)
        data = query.paginate(page=page, max_per_page=per_page, error_out=False).items
        return {"count": len(data), "items": [d.to_dict() for d in data]}, ok


@ns.route('/restaurants/search')
class RestaurantSearch(Resource):
    @ns.expect(search_args)
    def get(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        page, per_page = get_pagination_args(request.args)
        data, total = Restaurant.search(request.args["search_string"], page=page, per_page=per_page)
        items = [d.to_dict() for d in data.all()]
        return {"count": len(items), "total": total, "items": items}, ok
