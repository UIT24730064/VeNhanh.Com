from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='showing') # 'showing' hoặc 'upcoming'
    release_date = db.Column(db.Date) # Ngày khởi chiếu

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    show_time = db.Column(db.DateTime)
    price = db.Column(db.Float)

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer)
    seat_code = db.Column(db.String(5))
    status = db.Column(db.String(10), default="FREE")

class SeatHold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    expire_time = db.Column(db.DateTime)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    show_id = db.Column(db.Integer)
    seat_code = db.Column(db.String(5))
    total_price = db.Column(db.Float)