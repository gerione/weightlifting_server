"""
models.py
- Data classes for the api application
"""

from api import database as db
from flask_sqlalchemy import SQLAlchemy


class Current(db.Model):
    __tablename__ = 'current'

    id = db.Column(db.Integer, primary_key=True)
    lifter_id = db.Column(db.Integer, db.ForeignKey('lifters.id'))
    lifter = db.relationship("Lifter", backref="current")


class Competitions (db.Model):
    __tablename__ = 'competitions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    start_time = db.Column(db.DateTime)
    youtube_id = db.Column(db.String)
    type = db.Column(db.String)

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    location=self.location,
                    youtube_id=self.youtube_id,
                    start_time=str(self.start_time),
                    type=self.type)


class LifterMaster (db.Model):
    __tablename__ = 'liftermaster'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sex = db.Column(db.Boolean)

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    sex=self.sex)
class Lifter(db.Model):
    __tablename__ = 'lifters'

    id = db.Column(db.Integer, primary_key=True)
    lifter_id = db.Column(db.Integer, db.ForeignKey('liftermaster.id'))
    lifter = db.relationship("LifterMaster", backref="lifters")
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'))

    weight = db.Column(db.Float)
    sinclair_factor = db.Column(db.Float)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team = db.relationship("Team", backref="lifters")

    weightclass_id = db.Column(db.Integer, db.ForeignKey('weightclass.id'))
    weightclass = db.relationship("Weightclass", backref="lifters")

    lifts = db.relationship("Attempt", backref='lifters',  lazy=False)

    def to_dict(self):
        if not self.lifts:
            return dict(id=self.id,
                        lifter_id=self.lifter.id,
                        name=self.lifter.name,
                        sf=self.sinclair_factor,
                        sex=self.lifter.sex,
                        team=self.team.to_dict(),
                        weightclass=self.weightclass.to_dict(), lifts= [])

        return dict(id=self.id,
                    lifter_id=self.lifter.id,
                    name=self.lifter.name,
                    sf=self.sinclair_factor,
                    sex=self.lifter.sex,
                    team=self.team.to_dict(),
                    weightclass=self.weightclass.to_dict(),
                    lifts=[lift.to_dict() for lift in sorted(self.lifts, key=lambda x: x.attempt)])


class Team (db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    short = db.Column(db.String)

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    short=self.short)


class Weightclass (db.Model):
    __tablename__ = 'weightclass'

    id = db.Column(db.Integer, primary_key=True)

    sex = db.Column(db.Boolean)
    name = db.Column(db.String)
    min_weight = db.Column(db.Float)
    max_weight = db.Column(db.Float)

    def to_dict(self):
        return dict(id=self.id,
                    name=self.name,
                    min_weight=self.min_weight,
                    max_weight=self.max_weight,
                    sex=self.sex)

class Attempt(db.Model):
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)

    lifter_id = db.Column(db.Integer, db.ForeignKey('lifters.id'))

    weight = db.Column(db.Float)
    attempt = db.Column(db.Integer)
    result= db.Column(db.Integer)

    def to_dict(self):
        return dict(id=self.id,
                    weight=self.weight,
                    attempt=self.attempt,
                    result=self.result
                    )

