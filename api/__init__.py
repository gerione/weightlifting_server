"""
application.py
- creates a Flask app instance and registers the database object
"""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()
migrate = Migrate()


socketio = SocketIO(cors_allowed_origins="*")

def create_app(app_name='AUSTRIAN_WEIGHTLIFTING_OVERLAY_API'):
    app = Flask(app_name)
    app.config.from_object('api.config.BaseConfig')

    database.init_app(app)
    migrate.init_app(app, database)
    CORS(app)

    from api.api import api
    app.register_blueprint(api, url_prefix="/api")

    from api.models import db
    db.init_app(app)

    socketio.init_app(app)
    return app
