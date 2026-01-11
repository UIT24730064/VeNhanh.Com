from flask import Flask, render_template, url_for, request, redirect, send_file, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import qrcode
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'mot_chuoi_bi_mat_bat_ky'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODELS (GIỮ NGUYÊN) =================
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)

class Showtime:
    def __init__(self, id, movie, show_date, show_time, theater, price):
        self.id = id
        self.movie = movie
        self.show_date = show_date
        self.show_time = show_time
        self.theater = theater
        self.price = price

    def get_available_seats(self):
        return 60

class Booking:
    def __init__(self, booking_code, seat_numbers, quantity, total_price, showtime):
        self.booking_code = booking_code
        self.seat_numbers = seat_numbers
        self.quantity = quantity
        self.total_price = total_price
        self.showtime = showtime

# ================= MODELS (BỔ SUNG) =================
class ShowtimeDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    show_date = db.Column(db.Date)
    show_time = db.Column(db.Time)
    theater = db.Column(db.String(100))
    price = db.Column(db.Integer)

class SeatDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    showtime_id = db.Column(db.Integer)
    seat_code = db.Column(db.String(5))
    status = db.Column(db.String(10), default='available')  
    # available | holding | booked

class SeatHoldDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat_code = db.Column(db.String(5))
    session_id = db.Column(db.String(100))
    hold_until = db.Column(db.DateTime)

# ================= INIT DATA =================
with app.app_context():
    db.create_all()

    sample_movies = [
        {"title": "Nhà Hai Chủ", "image": "nha-hai-chu.jpg", "status": "showing"},
        {"title": "Thiên Đường Máu", "image": "thien-duong-mau.jpg", "status": "showing"},
        {"title": "Ai Thương Ai Mến", "image": "ai-thuong-ai-men.jpg", "status": "showing"},
        {"title": "Bằng Chứng Sinh Tử", "image": "bang-chung-sinh-tu.jpg", "status": "upcoming"},
        {"title": "Con Kể Ba Nghe", "image": "con-ke-ba-nghe.jpg", "status": "upcoming"},
        {"title": "Báu Vật Trời Cho", "image": "bau-vat-troi-cho.jpg", "status": "upcoming"}
    ]

    for m in sample_movies:
        if not Movie.query.filter_by(title=m['title']).first():
            db.session.add(Movie(**m))
    db.session.commit()

# ================= TTL FUNCTIONS =================
def hold_seat_ttl(seat_code):
    hold = SeatHoldDB(
        seat_code=seat_code,
        session_id=session.get('user', 'guest'),
        hold_until=datetime.now() + timedelta(minutes=5)
    )
    db.session.add(hold)
    db.session.commit()

def clear_expired_holds():
    now = datetime.now()
    expired = SeatHoldDB.query.filter(SeatHoldDB.hold_until < now).all()
    for h in expired:
        db.session.delete(h)
    db.session.commit()

# ================= ROUTES (GIỮ NGUYÊN + MỞ RỘNG) =================
@app.route('/')
def index():
    showing_movies = Movie.query.filter_by(status='showing').all()
    upcoming_movies = Movie.query.filter_by(status='upcoming').all()
    return render_template('index.html', showing_movies=showing_movies, upcoming_movies=upcoming_movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form.get('username')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['user'] = request.form.get('username')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/lich-chieu')
def lich_chieu():
    showing_movies = Movie.query.filter_by(status='showing').all()
    upcoming_movies = Movie.query.filter_by(status='upcoming').all()
    return render_template('lich_chieu.html', showing_movies=showing_movies, upcoming_movies=upcoming_movies)

@app.route('/rap-phim')
def rap_phim():
    return render_template('rap_phim.html')

@app.route('/khuyen-mai')
def khuyen_mai():
    return render_template('khuyen_mai.html')

@app.route('/showtimes/<int:movie_id>')
def show_showtimes(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    showtimes_list = [
        Showtime(1, movie, datetime(2026, 1, 15), datetime(2026, 1, 15, 9, 30), "CGV Quận 1", 75000),
        Showtime(2, movie, datetime(2026, 1, 15), datetime(2026, 1, 15, 12, 15), "CGV Quận 7", 85000),
        Showtime(3, movie, datetime(2026, 1, 15), datetime(2026, 1, 15, 15, 0), "CGV Thủ Đức", 85000),
    ]
    return render_template('showtime.html', movie=movie, showtimes=showtimes_list)

@app.route('/seats/<int:showtime_id>')
def seats(showtime_id):
    clear_expired_holds()

    movie_temp = Movie.query.first()
    st = Showtime(showtime_id, movie_temp, datetime.now(), datetime.now(), "Rạp 05", 85000)

    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    seats_by_row = {r: [{
        'code': f"{r}{i}",
        'type': 'vip' if r in ['E', 'F'] else 'normal',
        'status': 'available',
        'is_aisle': i == 5
    } for i in range(1, 11)] for r in rows}

    return render_template('seats.html', showtime=st, seats_by_row=seats_by_row)

@app.route('/book', methods=['POST'])
def book_tickets():
    seat_numbers = request.form.get('seat_numbers')
    showtime_id = request.form.get('showtime_id')

    if not seat_numbers:
        return redirect(url_for('index'))

    for seat in seat_numbers.split(','):
        hold_seat_ttl(seat)

    movie_temp = Movie.query.first()
    st = Showtime(showtime_id, movie_temp, datetime(2026, 1, 15), datetime(2026, 1, 15, 19, 0), "Rạp 05", 85000)

    num_seats = len(seat_numbers.split(','))
    booking_code = f"VN-{showtime_id}-{seat_numbers}"

    booking_info = Booking(
        booking_code=booking_code,
        seat_numbers=seat_numbers,
        quantity=num_seats,
        total_price=num_seats * 85000,
        showtime=st
    )

    return render_template('confirmation.html', booking=booking_info)

@app.route('/generate_qr/<booking_code>')
def generate_ticket_qr(booking_code):
    qr = qrcode.make(booking_code)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

# ================= ADMIN SHOWTIME (BỔ SUNG) =================
@app.route('/admin/showtimes')
def admin_showtimes():
    showtimes = ShowtimeDB.query.all()
    movies = Movie.query.all()
    return render_template('admin_showtimes.html', showtimes=showtimes, movies=movies)

if __name__ == '__main__':
    app.run(debug=True)
