import datetime
import os

from sqlalchemy import JSON, String, Text, Time, Integer

from app import db, flask_app
from app.models.model_base import ModelBase


class Restaurant(ModelBase):
    __tablename__ = "restaurant"

    serialize_only = (*ModelBase.serialize_only, "id", "user_id", "position", "description", "phone", "image_path",
                      "wday_opening", "wday_closing", "wend_opening", "wend_closing")

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, nullable=False)
    position = db.Column(JSON, nullable=False)
    description = db.Column(Text)
    phone = db.Column(String(120), unique=True, nullable=False)
    image_path = db.Column(String(200))

    wday_opening = db.Column(Time, nullable=False)
    wday_closing = db.Column(Time, nullable=False)
    wend_opening = db.Column(Time)
    wend_closing = db.Column(Time)

    @classmethod
    def validate_update(cls, rest_id, **attributes):
        obj = Restaurant.query.filter_by(id=rest_id).first()
        cls.validate_work_hours(attributes.get('wday_opening', obj.wday_opening),
                                attributes.get('wday_closing', obj.wday_closing))
        cls.validate_work_hours(attributes.get('wend_opening', obj.wend_opening),
                                attributes.get('wend_closing', obj.wend_closing))
        if 'phone' in attributes and attributes['phone'] != obj.phone and \
            cls.query.filter(phone=attributes['phone']).first() is not None:
            raise ValueError(f"Restaurant with phone number {attributes['phone']} already exist")

    @classmethod
    def update(cls, rest_id, **attributes):
        obj = Restaurant.query.filter_by(id=rest_id).first()

        if 'image_path' in attributes:
            if obj.image_path:
                old_path = os.path.abspath(os.path.join(flask_app.config['UPLOAD_FOLDER'], obj.image_path))
                if os.path.exists(old_path):
                    os.remove(old_path)
            obj.image_path = attributes['image_path']

        obj.phone = attributes.get('phone', obj.phone)
        obj.position = attributes.get('position', obj.position)
        obj.description = attributes.get('description', obj.description)

        obj.wday_opening = attributes.get('wday_opening', obj.wday_opening)
        obj.wday_closing = attributes.get('wday_closing', obj.wday_closing)
        obj.wend_opening = attributes.get('wend_opening', obj.wend_opening)
        obj.wend_closing = attributes.get('wend_closing', obj.wend_closing)
        db.session.commit()

    @staticmethod
    def validate_work_hours(opening_time: datetime.time, closing_time: datetime.time):
        if opening_time > closing_time:
            raise ValueError("")

