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


class Order(ModelBase):
    __tablename__ = "order"
    id = db.Column(Integer, primary_key=True)
    card_id = db.Column(Integer, nullable=False)
    restaurant_id = db.Column(Integer, nullable=False)
    status = db.Column(String(100), nullable=False, default=OrderStatus.opened.value[0])
    opened_time = db.Column(DateTime, default=datetime.datetime.utcnow())
    cooked_time = db.Column(DateTime, nullable=False)
    closed_time = db.Column(DateTime, nullable=False)

    @classmethod
    def validate_update(cls, **attributes):
        if 'restaurant_id' in attributes or 'card_id' in attributes or 'opened_time' in attributes or \
                'cooked_time' in attributes or 'closed_time' in attributes:
            raise ValueError("Unupdatable fields")
        if 'status' not in attributes:
            return

        if attributes['status'] not in OrderStatus.list():
            raise ValueError("Unsupported status")

        if OrderStatus[attributes['status']].value[1] < OrderStatus[cls.status].value[1]:
            raise ValueError("Could not set status that is prevent current status")

    @classmethod
    def update(cls, **attributes):
        if 'status' not in attributes:
            return
        status = OrderStatus[attributes['status']]
        if status == OrderStatus.opened:
            cls.opened_time = datetime.datetime.utcnow()
        if status.name == OrderStatus.cooked:
            cls.cooked_time = datetime.datetime.utcnow()
        if status.name == OrderStatus.closed or status.name == OrderStatus.cancelled:
            cls.closed_time = datetime.datetime.utcnow()

        cls.status = attributes['status']
        db.session.commit()
