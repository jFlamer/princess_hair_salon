from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Princess(db.Model):
    __tablename__ = 'princess'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movie = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    is_animated = db.Column(db.Boolean, nullable=False)
    rating = db.Column(db.Float, nullable=False)

    # Relationship for appointments
    appointments = db.relationship('Appointment', back_populates='princess')


class Hairstyle(db.Model):
    __tablename__ = 'hairstyle'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    duration = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)

    # Relationship for appointments
    appointments = db.relationship('Appointment', back_populates='hairstyle')


class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    princess_id = db.Column(db.Integer, db.ForeignKey('princess.id'), nullable=False)
    hairstyle_id = db.Column(db.Integer, db.ForeignKey('hairstyle.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default = False)

    # Define relationships with Princess and Hairstyle models
    princess = db.relationship('Princess', back_populates='appointments')
    hairstyle = db.relationship('Hairstyle', back_populates='appointments')
