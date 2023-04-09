from enum import Enum

from sqlalchemy import String, Text, Integer

from app import db
from app.models.model_base import ModelBase
from app.utils.exceptions import ITPUpdateError


class DishStatus(Enum):
    Active = "active"
    Unavailable = "unavailable"
    TempUnavailable = "temp unavailable"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Dish(ModelBase):
    __tablename__ = "dish"
    id = db.Column(Integer, primary_key=True)
    restaurant_id = db.Column(Integer, nullable=False)
    name = db.Column(String(120), nullable=False)
    description = db.Column(Text)
    status = db.Column(String(100), nullable=False)
    price = db.Column(Integer, nullable=False)

    @classmethod
    def create(cls, **attributes):
        dish = Dish(**attributes)
        db.session.add(dish)
        db.session.commit()
        return dish

    @classmethod
    def update(cls, **attributes):
        if "restaurant_id" in attributes:
            raise ValueError("")

        if 'status' in attributes:
            if attributes['status'] not in DishStatus.list():
                raise ITPUpdateError()
            cls.status = attributes['status']

        cls.name = attributes.get('name', default=cls.name)
        cls.description = attributes.get('description', default=cls.description)
        cls.price = attributes.get('price', default=cls.price)
        db.session.commit()
