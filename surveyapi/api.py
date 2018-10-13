"""
clients.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request
from .models import db, Lifter, Team, Weightclass, Attempt, Current


api = Blueprint('api', __name__)

@api.route('/lifters/flat/', methods=('GET', 'POST'))
def get_flat_lifters():
    lifters = Lifter.query.all()
    json_lifters = []
    for l in lifters:
        lifter = dict(id=l.id,
                    name=l.name,
                    weight=l.weight,
                    sf=l.sinclair_factor,
                    sex=l.sex,
                    team=l.team.to_dict(),
                    weightclass=l.weightclass.to_dict())
        i = 1
        for a in sorted(l.lifts, key=lambda x: x.attempt):
            att = a.to_dict()
            lifter['A'+str(i)] = att
            i = i+1

        while i<=6:
            lifter['A' + str(i)] = dict(id=i, attempt = i, weight=0,result=0)
            i = i + 1
        json_lifters.append(lifter)
    return jsonify(json_lifters)


def create_lifter(data, id=-99):
    if id != -99:
        lifter = Lifter.query.get(id)
    if lifter is None:
        lifter = Lifter(id=data['id'], name=data['name'].strip(), weight=data['weight'], sex=data['sex'])

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
            Weightclass.min_weight < lifter.weight).filter(Weightclass.max_weight >= lifter.weight).filter(Weightclass.sex == lifter.sex).first()
        if weightclass is None:
            weightclass = Weightclass.query.filter_by(name='default').first()
            if weightclass is None:
                weightclass = Weightclass(name='default', min_weight=0, max_weight=9999)
    lifter.weightclass = weightclass

    lifter.lifts = []
    for attempt in data['attempts']:
        a = Attempt(attempt=attempt['attempt'], weight=attempt['weight'], result=attempt['result'])
        lifter.lifts.append(a)
    return lifter

@api.route('/lifters/', methods=('GET', 'POST', 'DELETE'))
def lifters():
    if request.method == 'DELETE':
        lifters = Lifter.query.all()
        for l in lifters:
            db.session.delete(l)
        db.session.commit()
        return jsonify(dict()), 201
    elif request.method == 'GET':
        lifters = Lifter.query.all()
        return jsonify([l.to_dict() for l in lifters]), 201
    elif request.method == 'POST':
        lifter_data = request.get_json()

        for data in lifter_data['lifters']:
            lifter = create_lifter(data)
            db.session.add(lifter)
        db.session.commit()

        return jsonify(lifter.to_dict()), 201


@api.route('/lifters/<int:id>/', methods=('GET', 'PUT'))
def lifter(id):
    if request.method == 'GET':

        lifter = Lifter.query.get(id)
        return jsonify({'lifter': lifter.to_dict()})

    elif request.method == 'PUT':

        data = request.get_json()
        lifter = create_lifter(data,id)
        db.session.add(lifter)
        db.session.commit()

        return jsonify(lifter.to_dict()), 201


@api.route('/lifters/current/', methods=['GET'])
def get_current():
    current = Current.query.get(1)
    if current is None:
        return jsonify(error="Current not existing!"), 404
    elif current.lifter_id is None:
        return jsonify(error="Current not existing!"), 404
    else:
        return jsonify(current.lifter.to_dict()), 200


@api.route('/lifters/current/<int:id>', methods=['PUT'])
def set_current(id):
    current = Current.query.first()
    lifter = Lifter.query.get(id)
    if lifter is None:
        return jsonify(error="Lifter not existing"), 404
    if current is None:
        current = Current(id=1)
    current.lifter = lifter
    db.session.add(current)
    db.session.commit()

    return jsonify(lifter.to_dict()), 200


@api.route('/teams/', methods=('GET', 'POST', 'DELETE'))
def teams():
    if request.method == 'DELETE':
        teams = Team.query.all()
        for t in teams:
            db.session.delete(t)
        db.session.commit()
        return jsonify(dict()), 201
    elif request.method == 'GET':
        teams = Team.query.all()
        result = []
        for team in teams:
            team_total = 0
            team_snatch = 0
            team_cj = 0
            for lifter in team.lifters:
                attempts = Attempt.query.filter(Attempt.lifter_id == lifter.id, Attempt.result == 2)
                max_snatch = 0
                max_cj = 0
                for attempt in attempts:
                    if attempt.attempt < 4 and attempt.weight > max_snatch:
                        max_snatch = attempt.weight
                    if attempt.attempt > 3 and attempt.weight > max_cj:
                        max_cj = attempt.weight
                team_total = team_total + (max_snatch+max_cj)*lifter.sinclair_factor
                team_snatch= team_snatch + max_snatch*lifter.sinclair_factor
                team_cj = team_cj + max_cj*lifter.sinclair_factor

            team_result = dict(team.to_dict(), total=team_total, snatch=team_snatch, cj=team_cj)
            result.append(team_result)
        return jsonify(result)
    elif request.method == 'POST':
        data = request.get_json()
        for team_data in data['teams']:
            team = Team.query.get(team_data['id'])
            if team is None:
                team = Team(id=team_data['id'], name=team_data['name'], short=team_data['short'])

            db.session.add(team)
        db.session.commit()

        return jsonify(team.to_dict()), 201


@api.route('/weightclasses/', methods=('GET', 'POST'))
def weightclasses():
    if request.method == 'GET':
        weightclasses = Weightclass.query.all()
        return jsonify([w.to_dict() for w in weightclasses])
    elif request.method == 'POST':
        data = request.get_json()
        weightclass = Weightclass(name=data['name'], min_weight=data['min_weight'], max_weight=data['max_weight'])
        db.session.add(weightclass)
        db.session.commit()

        return jsonify(weightclass.to_dict()), 201


