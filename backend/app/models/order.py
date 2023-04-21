import datetime
from enum import Enum

from sqlalchemy import Integer, DateTime, String

from app import db
from app.models.model_base import ModelBase


class OrderStatus(Enum):
    opened = "opened", 0
    cooked = "cooked", 1
    closed = "closed", 2
    cancelled = "cancelled", 3

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value[0], cls))

    @classmethod
    def restaurant_options(cls):
        return [status for status in cls.list() if status != "opened"]

    @classmethod
    def client_options(cls):
        return ["cancelled"]


class Order(ModelBase):
    __tablename__ = "order"

    serialize_only = (*ModelBase.serialize_only, "id", "restaurant_id", "card_id", "status", "opened_time",
                      "cooked_time", "closed_time")

    id = db.Column(Integer, primary_key=True)
    card_id = db.Column(Integer, nullable=False)
    restaurant_id = db.Column(Integer, nullable=False)
    status = db.Column(String(100), nullable=False, default=OrderStatus.opened.value[0])
    opened_time = db.Column(DateTime, default=datetime.datetime.utcnow())
    cooked_time = db.Column(DateTime)
    closed_time = db.Column(DateTime)

    @classmethod
    def validate_update(cls, order_id, **attributes):
        if 'restaurant_id' in attributes or 'card_id' in attributes or 'opened_time' in attributes or \
                'cooked_time' in attributes or 'closed_time' in attributes:
            raise ValueError("Unupdatable fields")
        if 'status' not in attributes:
            return

        if attributes['status'] not in OrderStatus.list():
            raise ValueError("Unsupported status")

        obj = Order.query.filter_by(id=order_id).first()
        if OrderStatus[attributes['status']].value[1] < OrderStatus[obj.status].value[1]:
            raise ValueError("Could not set status that is prevent current status")

    @classmethod
    def update(cls, order_id, **attributes):
        if 'status' not in attributes:
            return
        obj = Order.query.filter_by(id=order_id).first()
        status = OrderStatus[attributes['status']]
        if status == OrderStatus.opened:
            obj.opened_time = datetime.datetime.utcnow()
        if status == OrderStatus.cooked:
            obj.cooked_time = datetime.datetime.utcnow()
        if status == OrderStatus.closed or status == OrderStatus.cancelled:
            obj.closed_time = datetime.datetime.utcnow()

        obj.status = attributes['status']
        db.session.commit()
