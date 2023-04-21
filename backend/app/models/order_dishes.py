from sqlalchemy import Integer

from app import db
from app.models.model_base import ModelBase


class OrderDishes(ModelBase):
    __tablename__ = "order_dish"

    serialize_only = (*ModelBase.serialize_only, "id", "order_id", "dish_id", "number")

    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, nullable=False)
    dish_id = db.Column(Integer, nullable=False)
    number = db.Column(Integer, nullable=False)
