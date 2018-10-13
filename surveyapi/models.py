"""
models.py
- Data classes for the surveyapi application
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Current(db.Model):
    __tablename__ = 'current'

    id = db.Column(db.Integer, primary_key=True)
    lifter_id = db.Column(db.Integer, db.ForeignKey('lifters.id'))
    lifter = db.relationship("Lifter", backref="current")

class Lifter(db.Model):
    __tablename__ = 'lifters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    weight = db.Column(db.Float)
    sinclair_factor = db.Column(db.Float)
    sex = db.Column(db.Boolean)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team = db.relationship("Team", backref="lifters")

    weightclass_id = db.Column(db.Integer, db.ForeignKey('weightclass.id'))
    weightclass = db.relationship("Weightclass", backref="lifters")

    lifts = db.relationship("Attempt", backref='lifters',  lazy=False)

    def to_dict(self):
        if not self.lifts:
            return dict(id=self.id,
                        name=self.name,
                        sf=self.sinclair_factor,
                        sex=self.sex,
                        team=self.team.to_dict(),
                        weightclass=self.weightclass.to_dict(), lifts= [])

        return dict(id=self.id,
                    name=self.name,
                    sf=self.sinclair_factor,
                    sex=self.sex,
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
                    max_weight=self.max_weight)

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

