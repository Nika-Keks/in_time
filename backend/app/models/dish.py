import os
from enum import Enum

from sqlalchemy import String, Text, Integer

from app import db, flask_app
from app.models.model_base import ModelBase
from app.utils.exceptions import ITPInvalidError
from app.utils.mixins import SearchableMixin


class DishStatus(Enum):
    Active = "active"
    Unavailable = "unavailable"
    TempUnavailable = "temp unavailable"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Dish(ModelBase, SearchableMixin):
    __tablename__ = "dish"
    __searchable__ = ["name", "description"]

    serialize_only = (*ModelBase.serialize_only, "id", "restaurant_id", "name", "description", "status", "price",
                      "image_path")

    id = db.Column(Integer, primary_key=True)
    restaurant_id = db.Column(Integer, nullable=False)
    name = db.Column(String(120), nullable=False)
    description = db.Column(Text)
    status = db.Column(String(100), nullable=False)
    price = db.Column(Integer, nullable=False)
    image_path = db.Column(String(200))

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

        if 'image_path' in attributes:
            if obj.image_path:
                old_path = os.path.abspath(os.path.join(flask_app.config['UPLOAD_FOLDER'], obj.image_path))
                if os.path.exists(old_path):
                    os.remove(old_path)
            obj.image_path = attributes['image_path']

        obj.name = attributes.get('name', obj.name)
        obj.description = attributes.get('description', obj.description)
        obj.price = attributes.get('price', obj.price)
        db.session.commit()
