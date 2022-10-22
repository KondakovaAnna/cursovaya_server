from enum import auto
from flask_sqlalchemy import SQLAlchemy

from run import db

class Plants(db.Model):
    __tablename__ = 'plants'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    info = db.Column(db.String(255), nullable=False)
    #histories = db.relationship('History', backref="plants")

