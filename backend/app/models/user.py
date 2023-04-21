from flask_login import UserMixin
from sqlalchemy import String, Integer
from werkzeug.security import generate_password_hash

from app import db, login_manager
from app.models.model_base import ModelBase


class User(ModelBase, UserMixin):
    __tablename__ = "user"

    serialize_only = (*ModelBase.serialize_only, "id", "name", "email")

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(120), nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password = db.Column(String(120), nullable=False)

    @classmethod
    def validate_update(cls, **attributes):
        if 'email' in attributes:
            if User.query.filter(email=attributes['email']).first() is not None:
                raise ValueError

    @classmethod
    def update(cls, user_id, **attributes):
        obj = User.query.filter_by(id=user_id).first()
        obj.name = attributes.get('name', obj.name)
        if 'password' in attributes:
            obj.password = generate_password_hash(attributes['password'], method='sha256')
        obj.email = attributes.get('email', obj.email)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
