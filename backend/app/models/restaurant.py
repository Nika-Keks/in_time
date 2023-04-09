import datetime

from sqlalchemy import JSON, String, Text, Time, Integer

from app import db
from app.models.model_base import ModelBase


class Restaurant(ModelBase):
    __tablename__ = "restaurant"
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer)
    position = db.Column(JSON)
    description = db.Column(Text)
    phone = db.Column(String(120), unique=True)

    wday_opening = db.Column(Time)
    wday_closing = db.Column(Time)
    wend_opening = db.Column(Time)
    wend_closing = db.Column(Time)

    @classmethod
    def validate_update(cls, **attributes):
        cls.validate_work_hours(attributes.get('wday_opening', default=cls.wday_opening),
                                attributes.get('wday_closing', default=cls.wday_closing))
        cls.validate_work_hours(attributes.get('wend_opening', default=cls.wend_opening),
                                attributes.get('wend_closing', default=cls.wend_closing))
        if 'phone' in attributes and attributes['phone'] != cls.phone and \
            cls.query.filter(phone=attributes['phone']).first() is not None:
            raise ValueError("")

    @classmethod
    def update(cls, **attributes):
        cls.phone = attributes.get('phone', default=cls.phone)
        cls.position = attributes.get('position', default=cls.position)
        cls.description = attributes.get('description', default=cls.description)

        cls.wday_opening = attributes.get('wday_opening', default=cls.wday_opening)
        cls.wday_closing = attributes.get('wday_closing', default=cls.wday_closing)
        cls.wend_opening = attributes.get('wend_opening', default=cls.wend_opening)
        cls.wend_closing = attributes.get('wend_closing', default=cls.wend_closing)
        db.session.commit()

    @staticmethod
    def validate_work_hours(opening_time: datetime.time, closing_time: datetime.time):
        if opening_time > closing_time:
            raise ValueError("")

