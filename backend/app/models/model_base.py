import datetime

from sqlalchemy import Integer, DateTime

from app import db


class ModelBase(db.Model):
    __abstract__ = True
    create_time = db.Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    update_time = db.Column(DateTime, nullable=False, default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<id {}>'.format(self.__class__.id)
