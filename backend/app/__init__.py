import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api


flask_app = Flask(__name__)
if 'APP_SETTINGS' in os.environ:
    flask_app.config.from_object(os.environ['APP_SETTINGS'])
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("ITP_DB_URI", default="postgresql://admin:qwer@localhost:5432/postgres")
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_app.secret_key = os.environ.get("ITP_SECRET_KEY", default="super secret key")
flask_app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)
login_manager = LoginManager(flask_app)
api = Api(flask_app)

from app import routes, models
