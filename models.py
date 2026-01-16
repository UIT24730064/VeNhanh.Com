from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# MOVIE
class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255))
    status = db.Column(db.String(20))  # showing | upcoming
    duration = db.Column(db.Integer)
    description = db.Column(db.Text)

    showtimes = db.relationship("ShowtimeDB", back_populates="movie")


# SHOWTIME
class ShowtimeDB(db.Model):
    __tablename__ = "showtimes"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)

    theater = db.Column(db.String(100))
    show_date = db.Column(db.Date)
    show_time = db.Column(db.Time)
    price = db.Column(db.Integer)

    movie = db.relationship("Movie", back_populates="showtimes")
    seats = db.relationship("SeatDB", backref="showtime", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", backref="showtime")


# SEAT
class SeatDB(db.Model):
    __tablename__ = "seats"

    id = db.Column(db.Integer, primary_key=True)
    showtime_id = db.Column(db.Integer, db.ForeignKey("showtimes.id"))

    seat_code = db.Column(db.String(5))
    seat_type = db.Column(db.String(20), default="Standard")
    status = db.Column(db.String(20), default="available")


# SEAT HOLD
class SeatHoldDB(db.Model):
    __tablename__ = "seat_holds"

    id = db.Column(db.Integer, primary_key=True)
    showtime_id = db.Column(db.Integer, db.ForeignKey("showtimes.id"))
    seat_code = db.Column(db.String(5))
    session_id = db.Column(db.String(100))
    hold_until = db.Column(db.DateTime)


# USER
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")

    bookings = db.relationship("Booking", back_populates="user")


# BOOKING
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(10), unique=True)

    showtime_id = db.Column(db.Integer, db.ForeignKey("showtimes.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    seat_numbers = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    payment_status = db.Column(db.String(20))

    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="bookings")
