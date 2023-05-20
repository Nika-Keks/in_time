from flask import request
from flask_login import current_user
from flask_restx import reqparse, Resource
from flask_restx.fields import String
from flask_restx.inputs import positive

from app import api, flask_app
from app.models.dish import Dish, DishStatus
from app.models.restaurant import Restaurant
from app.routes.utils import pagination_args, get_pagination_args
from app.utils.exceptions import ITPForbiddenError, ITPInvalidError, ok, created

ns = api.namespace('Dish', description='Operations with restaurants dishes')

get_args = pagination_args.copy()

create_args = reqparse.RequestParser()
create_args.add_argument('name', type=str, help='Dish name', required=True)
create_args.add_argument('description', type=str, help='Dish description', required=True)
create_args.add_argument('status', type=String(enum=DishStatus.list()), help='Dish status', required=True)
create_args.add_argument('price', type=positive, help='Dish price', required=True)

update_args = reqparse.RequestParser()
update_args.add_argument('name', type=str, help='Dish name')
update_args.add_argument('description', type=str, help='Dish description')
update_args.add_argument('status', type=String(enum=DishStatus.list()), help='Dish status')
update_args.add_argument('price', type=positive, help='Dish price')


# TODO: add filtering
@ns.route('/dishes')
class Dishes(Resource):
    @ns.expect(get_args)
    def get(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()
        page, per_page = get_pagination_args(request.args)
        data = [d.to_dict() for d in Dish.query.paginate(page=page, max_per_page=per_page, error_out=False).items]

        return {"count": len(data), "items": data}, ok


@ns.route('/dishes/<int:rest_id>')
class DishByRestaurant(Resource):
    @ns.expect(get_args)
    def get(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous or \
                Restaurant.query.filter_by(user_id=current_user.id, id=rest_id).first() is None:
            raise ITPForbiddenError()

        Restaurant.query.filter_by(id=rest_id).first_or_404(description=f"Restaurant with id {rest_id} was not found")

        page, per_page = get_pagination_args(request.args)
        dishes = Dish.query.filter_by(restaurant_id=rest_id).paginate(page=page, max_per_page=per_page, error_out=False).items
        return {"count": len(dishes), "items": [d.to_dict() for d in dishes]}, ok

    @ns.doc("Create new dish")
    @ns.expect(create_args)
    def post(self, rest_id):
        Restaurant.query.filter_by(id=rest_id).first_or_404(description=f"Restaurant with id {rest_id} was not found")

        if not current_user.is_authenticated or current_user.is_anonymous or \
                Restaurant.query.filter_by(user_id=current_user.id, id=rest_id).first() is None:
            raise ITPForbiddenError()

        dish = Dish.create(restaurant_id=rest_id, **request.args)
        return dish.to_dict(), created


@ns.route('/dishes/update/<int:dish_id>')
class DishById(Resource):
    @ns.expect(update_args)
    def put(self, dish_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        dish = Dish.query.filter_by(id=dish_id).first_or_404(description=f"Dish with id {dish_id} was not found")
        if Restaurant.query.filter_by(user_id=current_user.id, id=dish.restaurant_id).first() is None:
            raise ITPForbiddenError()

        try:
            Dish.update(dish_id, **request.args)
        except ValueError:
            raise ITPInvalidError()

        return dish.to_dict(), ok
