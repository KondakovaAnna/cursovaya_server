from enum import auto
from flask_sqlalchemy import SQLAlchemy

from run import db

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    #name = db.Column(db.String(255), nullable=False)
    login = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    #histories = db.relationship('History', back_populates="user_id")
