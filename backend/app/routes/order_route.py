from collections import defaultdict

from flask import request
from flask_login import current_user
from flask_restx import Resource, reqparse

from app import api, db
from app.models.dish import Dish
from app.models.order import Order, OrderStatus
from app.models.order_dishes import OrderDishes
from app.models.restaurant import Restaurant
from app.utils.exceptions import ITPForbiddenError, ITPUpdateError


def update_order_validation(order_id: int, request_args: dict):
    if not current_user.is_authenticated or current_user.is_anonymous:
        raise ITPForbiddenError()
    order = Order.query.filter_by(card_id=current_user.id, id=order_id).first_or_404()
    try:
        order.validate_update(request_args)
    except ValueError:
        raise ITPUpdateError()
    return order


input_dish = api.model('dish', {
    'id': int,
    'number': int
})
input_args = reqparse.RequestParser()
input_args.add_argument('dishes', type=input_dish, help='List of order dishes', required=True, action='append', default=[])


@api.route('/orders/user')
class UserOrder(Resource):
    # TODO: add filtering
    def get(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()
        # TODO: add getting by card id after creating Card model
        return Order.query.filter_by(card_id=current_user.id).all()

    @api.expect(input_args)
    @api.doc('Create order from user')
    def post(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        dishes_info = request.args.get('dishes')
        if not isinstance(dishes_info, list) or len(dishes_info) == 0:
            raise ITPUpdateError()

        dishes = [(Dish.query.filter_by(id=info["id"]).first_or_404(), info["number"]) for info in dishes_info]
        restaurant_order = defaultdict(list)
        for dish, count in dishes:
            restaurant_order[dish.restaurant_id].append((dish, count))

        orders = []
        for restaurant, dish, count in restaurant_order.items():
            order = Order(card_id=current_user.id, restaurant_id=restaurant)
            db.session.add(order)
            db.session.commit()
            orders.append(order)

            order_dish = OrderDishes(order_id=order.id, dish_id=dish.id, number=count)
            db.session.add(order_dish)
            db.session.commit()
        return orders


@api.route('/orders/user/<int:order_id>')
class UserOrderId(Resource):
    def get(self, order_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()
        return Order.query.filter_by(card_id=current_user.id, id=order_id).first_or_404()

    @api.param('status', type=str, help='New order status')
    def put(self, order_id):
        order = update_order_validation(order_id, request.args)
        status = request.args.get('status')
        if status is None:
            return order

        status = OrderStatus[status]
        is_user_changes = (status == OrderStatus.opened or status == OrderStatus.cancelled)
        if current_user.id != order.card_id or not is_user_changes:
            raise ITPForbiddenError()

        order.update(**request.args)
        return order


@api.route('/orders/restaurant/<int:rest_id>')
class RestaurantOrder(Resource):
    def get(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        restaurant = Restaurant.query.filter_by(user_id=current_user.id, id=rest_id).first()
        if restaurant is None:
            raise ITPForbiddenError()

        return Order.query.filter_by(restaurant_id=rest_id).all()


@api.route('/orders/restaurant/<int:rest_id>/<int:order_id>')
class RestaurantOrderId(Resource):
    @api.param('status', type=str, help='New order status')
    def put(self, rest_id, order_id):
        order = update_order_validation(order_id, request.args)

        status = request.args.get('status')
        if status is None:
            return order

        status = OrderStatus[status]
        user_restaurant = Restaurant.query.filter_by(user_id=current_user.id, id=order.restaurant_id).first()
        is_restaurant_changes = (
                status == OrderStatus.cooked or status == OrderStatus.closed or status == OrderStatus.canceled
        )
        if user_restaurant is None or not is_restaurant_changes:
            raise ITPForbiddenError()

        order.update(**request.args)
        return order
