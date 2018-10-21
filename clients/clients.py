"""
clients.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, render_template, request

pages = Blueprint('clients', __name__,template_folder='templates')


@pages.route('/')
def index():
    return render_template('overview.html'), 200

@pages.route('/scoreboard/team')
def get_scoreboard_team():
    return render_template('scoreboard.html', groupby="team.short"), 200

@pages.route('/scoreboard/')
def get_scoreboard():
    return render_template('scoreboard.html', groupby="weightclass.name"), 200


@pages.route('/team/')
def get_team():
    return render_template('team.html'), 200


@pages.route('/current/')
def get_current():
    return render_template('current.html'), 200