from enum import auto
from flask_sqlalchemy import SQLAlchemy

from run import db

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    plants_id = db.Column(db.Integer(), db.ForeignKey('plants.id'))
    peson = db.Column(db.Integer(), db.ForeignKey('users.id'))
    time = db.Column(db.DateTime())
    location_id = db.Column(db.Integer(), db.ForeignKey('location.id'))
    

