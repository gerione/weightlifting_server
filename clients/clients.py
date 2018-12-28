"""
clients.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, render_template, request

pages = Blueprint('clients', __name__, static_folder = "./dist/static", template_folder = "./dist")


@pages.route('/')
def index():
    return render_template('index.html'), 200

@pages.route('/', defaults={'path': ''})
@pages.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")