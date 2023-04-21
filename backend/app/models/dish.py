from enum import Enum

from sqlalchemy import String, Text, Integer

from app import db
from app.models.model_base import ModelBase
from app.utils.exceptions import ITPInvalidError


class DishStatus(Enum):
    Active = "active"
    Unavailable = "unavailable"
    TempUnavailable = "temp unavailable"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Dish(ModelBase):
    __tablename__ = "dish"

    serialize_only = (*ModelBase.serialize_only, "id", "restaurant_id", "name", "description", "status", "price")

    id = db.Column(Integer, primary_key=True)
    restaurant_id = db.Column(Integer, nullable=False)
    name = db.Column(String(120), nullable=False)
    description = db.Column(Text)
    status = db.Column(String(100), nullable=False)
    price = db.Column(Integer, nullable=False)

    @classmethod
    def create(cls, **attributes):
        if attributes['status'] not in DishStatus.list():
            raise ITPInvalidError(f"Incorrect dish status value. Acceptable values are: {DishStatus.list()}")
        dish = Dish(**attributes)
        db.session.add(dish)
        db.session.commit()
        return dish

    @classmethod
    def update(cls, dish_id, **attributes):
        obj = Dish.query.filter_by(id=dish_id).first()
        if "restaurant_id" in attributes:
            raise ValueError("")

        if 'status' in attributes:
            if attributes['status'] not in DishStatus.list():
                raise ITPInvalidError()
            obj.status = attributes['status']

        obj.name = attributes.get('name', obj.name)
        obj.description = attributes.get('description', obj.description)
        obj.price = attributes.get('price', obj.price)
        db.session.commit()
