from sqlalchemy import Integer

from app import db
from app.models.model_base import ModelBase


class OrderDishes(ModelBase):
    __tablename__ = "order_dish"
    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, nullable=False)
    dish_id = db.Column(Integer, nullable=False)
    number = db.Column(Integer, nullable=False)
