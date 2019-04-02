"""
clients.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request
from .models import db, Lifter, Team, Weightclass, Attempt, Current, Competitions, LifterMaster
from sqlalchemy import func
import datetime

api = Blueprint('api', __name__)


def find_or_create_lifter(data, id, competition_id):
    lifter_master = LifterMaster.query.get(id)
    if lifter_master is None:
        return -1

    lifter = Lifter.query.filter_by(lifter_id=id, competition_id=competition_id).first()
    if lifter is None:
        lifter = Lifter(lifter_id = lifter_master.id, weight=data['weight'])

    if 'team' in data:
        t = data['team']
        team = Team.query.get(t['id'])

        if team is None:
            team = Team.query.filter_by(name='default').first()
            if team is None:
                team = Team(name="default", short="")
    else:
        team = Team.query.filter_by(name='default').first()
        if team is None:
            team = Team(name="default", short="")
    lifter.team = team

    if 'sf' in data:
        lifter.sinclair_factor = data['sf']
    else:
        lifter.sinclair_factor = 1

    weightclass = None
    if 'Weightclass' in data:
        w = data['Weightclass']
        weightclass = Weightclass.query.filter_by(name=w['name']).first()

    if weightclass is None:
        weightclass = Weightclass.query.filter(
            (Weightclass.min_weight < lifter.weight) & (Weightclass.max_weight >= lifter.weight) & (Weightclass.sex == lifter_master.sex)).first()
        if weightclass is None:
            weightclass = Weightclass.query.filter_by(name='default').first()
            if weightclass is None:
                weightclass = Weightclass(name='default', min_weight=0, max_weight=9999)
    lifter.weightclass = weightclass

    lifter.lifts = []
    if "attempts" in data:
        for attempt in data['attempts']:
            a = Attempt(attempt=attempt['attempt'], weight=attempt['weight'], result=attempt['result'])
            lifter.lifts.append(a)
    else:
        for i in range(1,7,1):
            a = Attempt(attempt=i, weight=0, result=0)
            lifter.lifts.append(a)
    return lifter


@api.route('/lifters/<int:id>/', methods=('GET', 'PUT'))
def lifter(id):
    if request.method == 'GET':
        lifter = LifterMaster.query.get(id)
        if lifter == None:
            return jsonify(
                {
                    "errors": [
                        {
                            "status": 401,
                            "detail": "User with ID " + str(id) + " does not exist"
                        }
                    ]
                }
            ), 401
        return jsonify({'lifter': lifter.to_dict()})

    elif request.method == 'PUT':

        data = request.get_json()

        lifter = LifterMaster.query.get(id)
        if lifter is None:
            lifter = LifterMaster(id=id, name=data['name'].strip(), sex=data['sex'])
        else:
            lifter.name = data['name'].strip()
            lifter.sex = data['sex']
        db.session.add(lifter)
        db.session.commit()

        return jsonify(lifter.to_dict()), 201


@api.route('/lifters/', methods=['GET'])
def get_lifters():
    return jsonify({'lifters': [lifter.to_dict() for lifter in LifterMaster.query.all()]})


@api.route('/competitions/', methods=('GET', 'POST', 'DELETE'))
def competitions():
    if request.method == 'DELETE':
        for competition in Competitions.query.all():
            db.session.delete(competition)
        db.session.commit()
        return jsonify(dict()), 201
    elif request.method == 'GET':
        return jsonify([w.to_dict() for w in Competitions.query.all()])
    elif request.method == 'POST':
        data = request.get_json()
        if 'type' in data:
            type = data['name']
        else:
            type = 'single'
        if 'youtube_url' in data:
            youtube_url = data['youtube_url']
        else:
            youtube_url = ""

        competition = Competitions(name=data['name'], location=data['location'],
                                   start_time=datetime.datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M'), youtube_id=youtube_url, type=type)
        db.session.add(competition)
        db.session.commit()
        return jsonify(competition.to_dict()), 201


@api.route('/competitions/<int:id>/', methods=('GET', 'POST', 'DELETE', 'OPTIONS'))
def competition(id):
    if request.method == 'DELETE':
        competition = Competitions.query.get(id)
        db.session.delete(competition)
        db.session.commit()

    elif request.method == 'GET':
        competition = Competitions.query.get(id)
        return jsonify({'competition': competition.to_dict()})

    elif request.method == 'PUT':
        data = request.get_json()
        if 'type' in data:
            type = data['name']
        else:
            type = 'single'
        if 'youtube_url' in data:
            youtube_url = data['youtube_url']
        else:
            youtube_url = ""

        competition = Competitions(name=data['name'], location=data['location'],
                                   start_time=datetime.datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M'), youtube_id=youtube_url, type=type)
        db.session.add(competition)
        db.session.commit()
        return jsonify(competition.to_dict()), 201


@api.route('/competitions/<int:competition_id>/lifters/', methods=('GET', 'POST', 'DELETE'))
def lifters(competition_id):
    if request.method == 'DELETE':
        lifters = Lifter.query.filter_by(competition_id = competition_id)
        for l in lifters:
            db.session.delete(l)
        db.session.commit()
        return jsonify(dict()), 201
    elif request.method == 'GET':
        lifters = Lifter.query.filter_by(competition_id = competition_id)
        result = []
        for lifter in lifters:
            max_snatch = db.session.query(func.max(Attempt.weight)).filter(Attempt.lifter_id == lifter.id).filter(
                Attempt.attempt < 4).filter(Attempt.result == 2).first()[0]
            max_cj = db.session.query(func.max(Attempt.weight)).filter(Attempt.lifter_id == lifter.id).filter(
                Attempt.attempt > 3).filter(Attempt.result == 2).first()[0]

            lifterdata = lifter.to_dict()
            lifterdata.update({'max_snatch': max_snatch})
            lifterdata.update({'max_cj': max_cj })
            lifterdata.update({'snatch_points': max_snatch*lifter.sinclair_factor})
            lifterdata.update({'cj_points': max_cj * lifter.sinclair_factor})
            lifterdata.update({'total_points': (max_snatch+max_cj) * lifter.sinclair_factor})
            result.append(lifterdata)

        return jsonify(result), 201
    elif request.method == 'POST':
        if Competitions.query.get(competition_id) is None:
            return jsonify("Compettiion not existing", 401)

        lifter_data = request.get_json()

        for data in lifter_data['lifters']:
            lifter = find_or_create_lifter(data, data["id"], competition_id)
            if lifter == -1:
                return jsonify(
                    {
                        "errors": [
                            {
                                "status": 401,
                                "detail": "Master data of user with ID " + str(id) + " does not exist"
                            }
                        ]
                    }
                ), 401
            lifter.competition_id = competition_id
            db.session.add(lifter)
        db.session.commit()

        return jsonify(lifter.to_dict()), 201


@api.route('/competitions/<int:competition_id>/lifters/<int:lifter_id>/', methods=('PUT', 'DELETE'))
def lifters_update(competition_id,lifter_id):
    if request.method == 'PUT':
        if Competitions.query.get(competition_id) is None:
            return jsonify("Compettiion not existing", 401)

        data = request.get_json()
        lifter = find_or_create_lifter(data, data["id"], competition_id)
        if lifter == -1:
            return jsonify(
                {
                    "errors": [
                        {
                            "status": 401,
                            "detail": "Master data of user with ID " + str(id) + " does not exist"
                        }
                    ]
                }
            ), 401
        lifter.competition_id = competition_id
        db.session.add(lifter)
        db.session.commit()

        return jsonify(lifter.to_dict()), 201


@api.route('/competitions/<int:competition_id>/lifters/flat/', methods=('GET', 'POST'))
def get_flat_lifters(competition_id):
    lifters = Lifter.query.filter_by(competition_id=competition_id)
    json_lifters = []
    for l in lifters:
        lifter = dict(id=l.id,
                    name=l.lifter.name,
                    weight=l.weight,
                    sf=l.sinclair_factor,
                    sex=l.lifter.sex,
                    team=l.team.to_dict(),
                    weightclass=l.weightclass.to_dict())
        i = 1
        for a in sorted(l.lifts, key=lambda x: x.attempt):
            att = a.to_dict()
            lifter['A'+str(i)] = att
            i = i+1

        while i <= 6:
            lifter['A' + str(i)] = dict(id=i, attempt = i, weight=0,result=0)
            i = i + 1
        json_lifters.append(lifter)
    return jsonify(json_lifters)


@api.route('/competitions/<int:competition_id>/lifters/current/', methods=['GET'])
def get_current(competition_id):

    current = Current.query.filter(Current.lifter.has(competition_id=competition_id)).first()
    if current is None:
        return jsonify(error="Current not existing!"), 401
    elif current.lifter_id is None:
        return jsonify(error="Current not existing!"), 401
    else:
        return jsonify(current.lifter.to_dict()), 200


@api.route('/competitions/<int:competition_id>/lifters/<int:id>/current/', methods=['PUT'])
def set_current(competition_id, id):

    current = Current.query.filter(Current.lifter.has(competition_id=competition_id)).first()
    if current is None:
        current = Current()
    lifter = Lifter.query.filter_by(lifter_id=id, competition_id=competition_id).first()
    if lifter is None:
        return jsonify(error="Lifter not existing"), 404

    current.lifter = lifter
    db.session.add(current)
    db.session.commit()

    return jsonify(lifter.to_dict()), 200


@api.route('/competitions/<int:competition_id>/teams/', methods=['GET'])
def teams_forecast(competition_id):

    teams = Team.query.join(Lifter).filter(Lifter.competition_id == competition_id).all()
    result = []
    for team in teams:
        team_total = 0
        team_snatch = 0
        team_cj = 0

        team_total_forecast = 0
        team_snatch_forecast = 0
        team_cj_forecast = 0
        for lifter in team.lifters:
            max_snatch = db.session.query(func.max(Attempt.weight)).filter(Attempt.lifter_id == lifter.id).filter(
                Attempt.attempt < 4).filter(Attempt.result == 2).first()[0]
            max_cj = db.session.query(func.max(Attempt.weight)).filter(Attempt.lifter_id == lifter.id).filter(
                Attempt.attempt > 3).filter(Attempt.result == 2).first()[0]
            if max_snatch == None:
                max_snatch = 0
            if max_cj == None:
                max_cj = 0
            team_total = team_total + (max_snatch + max_cj) * lifter.sinclair_factor
            team_snatch = team_snatch + max_snatch * lifter.sinclair_factor
            team_cj = team_cj + max_cj * lifter.sinclair_factor

            max_snatch_forecast = db.session.query(func.max(Attempt.weight)).filter(Attempt.lifter_id == lifter.id).filter(Attempt.attempt < 4).filter((Attempt.result == 0) | (Attempt.result == 2)).first()[0]
            max_cj_forecast = db.session.query(func.max(Attempt.weight)).filter(Attempt.lifter_id == lifter.id).filter(Attempt.attempt > 3).filter((Attempt.result == 0) | (Attempt.result == 2)).first()[0]

            team_total_forecast = team_total_forecast + (max_snatch_forecast+max_cj_forecast)*lifter.sinclair_factor
            team_snatch_forecast= team_snatch_forecast + max_snatch_forecast*lifter.sinclair_factor
            team_cj_forecast = team_cj_forecast + max_cj_forecast*lifter.sinclair_factor

        team_result = dict(team.to_dict(), total_forecast=team_total_forecast, snatch_forecast=team_snatch_forecast, cj_forecast=team_cj_forecast, total=team_total, snatch=team_snatch, cj=team_cj)
        result.append(team_result)
    return jsonify(result)

@api.route('/weightclasses/', methods=('GET', 'POST', 'DELETE'))
def weightclasses():
    if request.method == 'DELETE':
        weightclasses = Weightclass.query.all()
        for w in weightclasses:
            db.session.delete(w)
        db.session.commit()
        return jsonify(dict()), 201
    elif request.method == 'GET':
        weightclasses = Weightclass.query.all()
        return jsonify([w.to_dict() for w in weightclasses])
    elif request.method == 'POST':
        data = request.get_json()
        weightclass = Weightclass(name=data['name'], min_weight=data['min_weight'], max_weight=data['max_weight'], sex=data['sex'])
        db.session.add(weightclass)
        db.session.commit()

        return jsonify(weightclass.to_dict()), 201



