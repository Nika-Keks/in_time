from flask_login import UserMixin
from sqlalchemy import String, Integer
from werkzeug.security import generate_password_hash

from app import db, login_manager
from app.models.model_base import ModelBase


class User(ModelBase, UserMixin):
    __tablename__ = "user"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(120))
    email = db.Column(String(120), unique=True)
    password = db.Column(String(120), nullable=False)

    @classmethod
    def validate_update(cls, **attributes):
        if 'email' in attributes:
            if User.query.filter(email=attributes['email']).first() is not None:
                raise ValueError

    @classmethod
    def update(cls, **attributes):
        cls.name = attributes.get('name', default=cls.name)
        if 'password' in attributes:
            cls.password = generate_password_hash(attributes['password'], method='sha256')
        cls.email = attributes.get('email', default=cls.email)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

