import datetime

from sqlalchemy import DateTime

from app import db
from app.utils.mixins import CustomSerializerMixin


class ModelBase(db.Model, CustomSerializerMixin):
    __abstract__ = True

    serialize_only = ('create_time', 'update_time')

    create_time = db.Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    update_time = db.Column(DateTime, nullable=False, default=datetime.datetime.utcnow(),
                            onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return '<id {}>'.format(self.__class__.id)
