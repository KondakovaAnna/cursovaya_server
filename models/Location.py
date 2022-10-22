from enum import auto
from flask_sqlalchemy import SQLAlchemy

from run import db

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float(), primary_key=True)
    longitude = db.Column(db.Float(), primary_key=True)
    #histories = db.relationship('History', back_populates="location")