from collections import defaultdict

from flask import request
from flask_login import current_user
from flask_restx import Resource, reqparse, fields
from flask_restx.fields import String

from app import api, db
from app.models.dish import Dish
from app.models.order import Order, OrderStatus
from app.models.order_dishes import OrderDishes
from app.models.restaurant import Restaurant
from app.utils.exceptions import ITPForbiddenError, ITPInvalidError, ok, created


def update_order_validation(order_id: int, request_args: dict):
    if not current_user.is_authenticated or current_user.is_anonymous:
        raise ITPForbiddenError()
    order = Order.query.filter_by(id=order_id).first_or_404(
        f"Order with id {order_id} was not found")
    try:
        Order.validate_update(order_id, **request_args)
    except ValueError:
        raise ITPInvalidError()
    return order


user_ns = api.namespace('User orders', description='Operations with current logged in user orders')
rest_ns = api.namespace('Restaurant orders', description='Operations with restaurant orders')

input_dish = api.model('dish', {
    'id': fields.Integer,
    'number': fields.Integer
})
input_args = reqparse.RequestParser()
input_args.add_argument('dishes', type=input_dish, help='List of order dishes', required=True, action='append', default=[])


update_rest_args = reqparse.RequestParser()
update_rest_args.add_argument('status', type=String(enum=OrderStatus.restaurant_options()), help='New order status')

update_user_args = reqparse.RequestParser()
update_user_args.add_argument('status', type=String(enum=OrderStatus.client_options()), help='New order status')


@user_ns.route('/orders/user')
class UserOrder(Resource):
    # TODO: add filtering
    def get(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()
        # TODO: add getting by card id after creating Card model
        data = Order.query.filter_by(card_id=current_user.id).all()
        return {"count": len(data), "items": [d.to_dict() for d in data]}, ok

    @user_ns.expect([input_dish])
    @user_ns.doc('Create order from user')
    def post(self):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        dishes_info = request.get_json()
        if not isinstance(dishes_info, list) or len(dishes_info) == 0:
            raise ITPInvalidError()

        dishes = [(Dish.query.filter_by(id=info["id"]).first_or_404(f"Dish with id {info['id']} was not found"),
                   info["number"]) for info in dishes_info]
        restaurant_order = defaultdict(list)
        for dish, count in dishes:
            restaurant_order[dish.restaurant_id].append((dish, count))

        orders = []
        for restaurant, info in restaurant_order.items():
            for dish, count in info:
                order = Order(card_id=current_user.id, restaurant_id=restaurant)
                db.session.add(order)
                db.session.commit()
                orders.append(order.to_dict())

                order_dish = OrderDishes(order_id=order.id, dish_id=dish.id, number=count)
                db.session.add(order_dish)
                db.session.commit()
        return {"count": len(orders), "items": orders}, created


@user_ns.route('/orders/user/<int:order_id>')
class UserOrderId(Resource):
    def get(self, order_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()
        return Order.query.filter_by(card_id=current_user.id, id=order_id).first_or_404(
            f"Order with id {order_id} for user {current_user.id} was not found").to_dict(), ok

    @user_ns.expect(update_user_args)
    def put(self, order_id):
        order = Order.query.filter_by(id=order_id, card_id=current_user.id).first_or_404(
            f"Order with id {order_id} for user was not found")
        update_order_validation(order_id, request.args)
        status = request.args.get('status')
        if status is None:
            return order.to_dict(), ok

        status = OrderStatus[status]
        is_user_changes = (status == OrderStatus.opened or status == OrderStatus.cancelled)
        if current_user.id != order.card_id or not is_user_changes:
            raise ITPForbiddenError()

        Order.update(order_id, **request.args)
        return order.to_dict(), ok


@rest_ns.route('/orders/restaurant/<int:rest_id>')
class RestaurantOrder(Resource):
    def get(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        restaurant = Restaurant.query.filter_by(user_id=current_user.id, id=rest_id).first()
        if restaurant is None:
            raise ITPForbiddenError()

        data = Order.query.filter_by(restaurant_id=rest_id).all()
        return {"count": len(data), "items": [d.to_dict() for d in data]}, ok


@rest_ns.route('/orders/restaurant/<int:rest_id>/<int:order_id>')
class RestaurantOrderId(Resource):
    @rest_ns.expect(update_rest_args)
    def put(self, rest_id, order_id):
        order = update_order_validation(order_id, request.args)

        status = request.args.get('status')
        if status is None:
            return order.to_dict(), ok

        status = OrderStatus[status]
        user_restaurant = Restaurant.query.filter_by(user_id=current_user.id, id=order.restaurant_id).first()
        is_restaurant_changes = (
                status == OrderStatus.cooked or status == OrderStatus.closed or status == OrderStatus.canceled
        )
        if user_restaurant is None or not is_restaurant_changes:
            raise ITPForbiddenError()

        Order.update(order_id, **request.args)
        return order.to_dict(), ok
