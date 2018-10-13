"""
application.py
- creates a Flask app instance and registers the database object
"""

from flask import Flask
from flask_cors import CORS

def create_app(app_name='AUSTRIAN_WEIGHTLIFTING_OVERLAY_API'):
    app = Flask(app_name)
    app.config.from_object('surveyapi.config.BaseConfig')

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    from surveyapi.api import api
    app.register_blueprint(api, url_prefix="/api")

    from clients.clients import pages
    app.register_blueprint(pages, url_prefix="/pages")

    from surveyapi.models import db
    db.init_app(app)

    return app
