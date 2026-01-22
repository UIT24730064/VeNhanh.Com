from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    flash, send_file, make_response)
from models import (db, Movie, ShowtimeDB, SeatDB, SeatHoldDB, Booking, User)
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, date, timezone
from io import BytesIO, StringIO
import uuid
import qrcode
from sqlalchemy import func, text
import csv
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# CẤU HÌNH APP
app = Flask(__name__)
app.secret_key = "secret_key_demo_123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cinema.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Tạo danh sách 7 ngày tới để hiển thị lịch chiếu
date_list = []
for i in range(7):
    d = date.today() + timedelta(days=i)
    date_list.append({
        'str': d.strftime('%Y-%m-%d'),
        'day_name': 'Hôm nay' if i == 0 else d.strftime('%a'),
        'date_num': d.strftime('%d/%m')
    })

# KHỞI TẠO DATABASE 
with app.app_context():
    db.create_all()
    if not Movie.query.first():
        sample_movies = [
            {
                "title": "Nhà Hai Chủ", 
                "image": "nha-hai-chu.jpg", 
                "status": "showing",
                "duration": 120, 
                "description": "Câu chuyện kịch tính về những bí mật ẩn giấu trong một gia đình thượng lưu."
            },
            {
                "title": "Thiên Đường Máu", 
                "image": "thien-duong-mau.jpg", 
                "status": "showing",
                "duration": 105,
                "description": "Hành trình tìm kiếm sự thật đằng sau những vụ mất tích bí ẩn tại vùng quê."
            },
            {
                "title": "Ai Thương Ai Mến", 
                "image": "ai-thuong-ai-men.jpg", 
                "status": "showing",
                "duration": 95,
                "description": "Bộ phim tình cảm nhẹ nhàng về những rung động đầu đời."
            },
            {
                "title": "Con Kể Ba Nghe", 
                "image": "con-ke-ba-nghe.jpg", 
                "status": "showing",
                "duration": 110,
                "description": "Tình cảm cha con ấm áp và những bài học cuộc sống quý giá."
            },
            # Dữ liệu phim Sắp chiếu (Upcoming)
            {
                "title": "Nhà Trấn Quỷ", 
                "image": "nha-tran-quy.jpg", 
                "status": "upcoming", 
                "duration": 110, 
                "description": "Câu chuyện kinh dị tâm linh về một ngôi nhà bị nguyền rủa."
            },
            {
                "title": "Bằng Chứng Sinh Tử", 
                "image": "bang-chung-sinh-tu.jpg", 
                "status": "upcoming", 
                "duration": 130, 
                "description": "Cuộc rượt đuổi nghẹt thở để tìm ra sự thật đằng sau vụ án chấn động."
            },
            {
                "title": "Con Kể Ba Nghe", 
                "image": "con-ke-ba-nghe.jpg", 
                "status": "upcoming", 
                "duration": 95, 
                "description": "Những mẩu chuyện nhỏ ấm áp về tình cảm gia đình."
            },
            {
                "title": "Báu Vật Trời Cho", 
                "image": "bau-vat-troi-cho.jpg", 
                "status": "upcoming", 
                "duration": 100, 
                "description": "Bộ phim hài hước về chuyến phiêu lưu tìm kho báu bất ngờ."
            }
        ]
        for m in sample_movies:
            db.session.add(Movie(**m))
        db.session.commit()
        print(">>> Khởi tạo dữ liệu phim thành công!")

# TẠO DATA SUẤT CHIẾU MẪU
with app.app_context():
    db.create_all()
  

    # Kiểm tra nếu chưa có suất chiếu nào thì mới tạo
    if not ShowtimeDB.query.first():
        showing_movies = Movie.query.filter_by(status='showing').all()
        
        theaters = [
            "CGV Lê Thánh Tôn", 
            "CGV Quận 7", 
            "CGV Thủ Đức"
        ]
        
        # Danh sách các khung giờ chiếu cố định
        time_slots = ["08:30", "10:45", "15:30", "20:15", "22:30"]

        for movie in showing_movies:
            # Tạo suất chiếu cho 7 ngày tới (từ hôm nay)
            for i in range(7):
                show_date = date.today() + timedelta(days=i)
                
                for theater in theaters:
                    # Mỗi phim tại mỗi rạp chọn ra 3-4 khung giờ ngẫu nhiên hoặc cố định
                    # Ở đây chọn khung giờ so le để tránh trùng lịch quá nhiều
                    selected_slots = time_slots[::2] if (movie.id + i) % 2 == 0 else time_slots[1::2]
                    
                    for t_str in selected_slots:
                        show_time = datetime.strptime(t_str, "%H:%M").time()
                        
                        # Tính giá vé: Cuối tuần (T7, CN) hoặc sau 17h giá 95k, còn lại 75k
                        is_weekend = show_date.weekday() >= 5
                        is_evening = show_time.hour >= 17
                        price = 95000 if (is_weekend or is_evening) else 75000
                        
                        new_st = ShowtimeDB(
                            movie_id=movie.id,
                            show_date=show_date,
                            show_time=show_time,
                            theater=theater,
                            price=price
                        )
                        db.session.add(new_st)
        
        db.session.commit()
        print(">>> Đã tạo thành công dữ liệu suất chiếu chuyên nghiệp cho các phim đang chiếu!")

# TIỆN ÍCH

def create_super_admin():
    with app.app_context():
        # Kiểm tra xem admin đã tồn tại chưa để tránh trùng lặp
        admin_exists = User.query.filter_by(username="admin").first()
        
        if not admin_exists:
            hashed_pw = generate_password_hash("admin123", method='pbkdf2:sha256')
            new_admin = User(
                username="admin",
                password=hashed_pw,
                role="admin"  # Cực kỳ quan trọng: gán quyền admin ở đây
            )
            db.session.add(new_admin)
            db.session.commit()
            print("✅ Đã tạo tài khoản Admin thành công!")
            print("👤 Username: admin")
            print("🔑 Password: admin123")
        else:
            print("⚠️ Tài khoản admin đã tồn tại.")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra xem đã đăng nhập chưa và role có phải là admin không
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Bạn không có quyền truy cập trang này!", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def clear_expired_holds():
    now = datetime.now()
    expired = SeatHoldDB.query.filter(SeatHoldDB.hold_until < now).all()

    for h in expired:
        seat = SeatDB.query.filter_by(
            showtime_id=h.showtime_id,
            seat_code=h.seat_code
        ).first()

        if seat and seat.status == "holding":
            seat.status = "available"

        db.session.delete(h)

    db.session.commit()


# ROUTES CHÍNH
@app.route("/")
def index():
    showing = Movie.query.filter_by(status='showing').all()
    upcoming = Movie.query.filter_by(status='upcoming').all()
    return render_template("index.html", showing_movies=showing, upcoming_movies=upcoming)

@app.route('/save_socket_sid', methods=['POST'])
def save_socket_sid():
    data = request.get_json()
    session['socket_sid'] = data.get('sid') # Lưu SID hiện tại vào session
    return {"status": "ok"}

# ĐĂNG NHẬP / ĐĂNG KÝ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') # Lấy thêm password
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password): # Kiểm tra hash
            session['user_id'] = user.id
            session['user'] = user.username
            session['role'] = user.role
            flash(f"Chào mừng {username}!", "success")
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại!", "danger")
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, role="user")
        db.session.add(new_user)
        db.session.commit()
        
        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for('index'))

# LỊCH CHIẾU & GHẾ NGỒI

@app.route("/movie/<int:movie_id>/showtimes")
def show_showtimes(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # 1. Tạo danh sách 7 ngày tới để hiển thị thanh chọn ngày
    date_list = []
    for i in range(7):
        d = date.today() + timedelta(days=i)
        date_list.append({
            'obj': d,
            'str': d.strftime('%Y-%m-%d'),
            'display': d.strftime('%d/%m')
        })

    # 2. Lấy ngày được chọn từ URL, mặc định là hôm nay
    selected_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = date.today()

    # 3. Lọc suất chiếu: Chỉ lấy các suất chưa diễn ra nếu là ngày hôm nay
    now = datetime.now()
    query = ShowtimeDB.query.filter_by(movie_id=movie_id, show_date=selected_date)
    
    if selected_date == date.today():
        # Chỉ lấy suất chiếu có giờ lớn hơn giờ hiện tại
        st_list = query.filter(ShowtimeDB.show_time > now.time()).order_by(ShowtimeDB.show_time).all()
    else:
        st_list = query.order_by(ShowtimeDB.show_time).all()

    return render_template(
        "showtime.html", 
        movie=movie, 
        showtimes=st_list, 
        date_list=date_list, 
        selected_date=selected_date_str,
        now=now
    )

@app.route("/seats/<int:showtime_id>")
def seats(showtime_id):
    clear_expired_holds()
    st = ShowtimeDB.query.get_or_404(showtime_id)
    all_seats = SeatDB.query.filter_by(showtime_id=showtime_id).all()

    # Tự động tạo sơ đồ nếu chưa tồn tại
    if not all_seats:
        for r in ["A", "B", "C", "D", "E", "F"]:
            # Logic: Hàng E và F là ghế VIP
            s_type = "VIP" if r in ["E", "F"] else "Standard"
            for i in range(1, 11):
                db.session.add(SeatDB(
                    showtime_id=showtime_id, 
                    seat_code=f"{r}{i}",
                    seat_type=s_type
                ))
        db.session.commit()
        return redirect(url_for("seats", showtime_id=showtime_id))
    
    seat_map = {}
    for s in all_seats:
        row_letter = s.seat_code[0]
        if row_letter not in seat_map: 
            seat_map[row_letter] = []
        seat_map[row_letter].append({
            "code": s.seat_code, 
            "status": s.status,
            "type": s.seat_type
        })
    return render_template("seats.html", showtime=st, seats_by_row=seat_map)

# THANH ĐIỀU HƯỚNG BỔ SUNG

@app.route("/he-thong-rap")
def rap_phim():
    return render_template("rap_phim.html")

@app.route("/khuyen-mai")
def khuyen_mai():
    return render_template("khuyen_mai.html")

@app.route("/my-tickets")
def my_tickets():
    if 'user' not in session:
        flash("Vui lòng đăng nhập để xem vé!", "warning")
        return redirect(url_for('login'))
    user_bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template("my_tickets.html", bookings=user_bookings)

# GIỮ GHẾ

@socketio.on("release_seat")
def handle_release_seat(data):
    showtime_id = data["showtime_id"]
    seat_code = data["seat_code"]

    seat = SeatDB.query.filter_by(
        showtime_id=showtime_id,
        seat_code=seat_code
    ).first()

    if seat:
        seat.status = "available"

        SeatHoldDB.query.filter_by(
            showtime_id=showtime_id,
            seat_code=seat_code
        ).delete()

        db.session.commit()

        emit("seat_update", {
            "seat_code": seat_code,
            "status": "available"
        }, broadcast=True)

@socketio.on("hold_seat")
def handle_hold_seat(data):
    showtime_id = data["showtime_id"]
    seat_code = data["seat_code"]
    sid = request.sid

    seat = SeatDB.query.filter_by(
        showtime_id=showtime_id,
        seat_code=seat_code
    ).first()

    if not seat or seat.status != "available":
        emit("hold_failed", {"seat_code": seat_code}, room=sid)
        return

    # Cập nhật DB
    seat.status = "holding"

    hold = SeatHoldDB(
        showtime_id=showtime_id,
        seat_code=seat_code,
        session_id=sid,
        hold_until=datetime.now() + timedelta(minutes=5)
    )
    db.session.add(hold)
    db.session.commit()

    
    emit("hold_success", {
        "seat_code": seat_code
    }, room=sid)

    
    emit("seat_update", {
        "seat_code": seat_code,
        "status": "holding"
    }, include_self=False)


# THANH TOÁN & QR CODE

@app.route("/book_tickets", methods=["POST"])
def book_tickets():
    clear_expired_holds()
    if "user_id" not in session:
        flash("Vui lòng đăng nhập!", "danger")
        return redirect(url_for("login"))

    showtime_id = int(request.form["showtime_id"])
    seats_selected = request.form.get("seat_numbers", "").split(",")

    if not seats_selected or seats_selected == [""]:
        flash("Bạn chưa chọn ghế!", "danger")
        return redirect(url_for("seats", showtime_id=showtime_id))

    st = ShowtimeDB.query.get_or_404(showtime_id)

    booked_seats = []
    total_price = 0

    for scode in seats_selected:
        hold = SeatHoldDB.query.filter(
            SeatHoldDB.showtime_id == showtime_id,
            SeatHoldDB.seat_code == scode,
            SeatHoldDB.hold_until > datetime.now()
        ).first()

        if not hold:
            flash(f"Ghế {scode} không còn hợp lệ", "danger")
            return redirect(url_for("seats", showtime_id=showtime_id))

        seat = SeatDB.query.filter_by(
            showtime_id=showtime_id,
            seat_code=scode
        ).first()

        if seat.status != "holding":
            flash(f"Ghế {scode} đã được đặt", "danger")
            return redirect(url_for("seats", showtime_id=showtime_id))

        booked_seats.append(seat)

    
    for seat in booked_seats:
        seat.status = "booked"
        total_price += st.price + (20000 if seat.seat_type == "VIP" else 0)

        socketio.emit("seat_update", {
            "seat_code": seat.seat_code,
            "status": "booked"
        }, to=True)

    SeatHoldDB.query.filter(
        SeatHoldDB.showtime_id == showtime_id,
        SeatHoldDB.seat_code.in_(seats_selected)
    ).delete(synchronize_session=False)

    booking = Booking(
        booking_code=str(uuid.uuid4())[:8].upper(),
        showtime_id=showtime_id,
        user_id=session["user_id"],
        seat_numbers=",".join(seats_selected),
        quantity=len(seats_selected),
        total_price=total_price,
        payment_status="Paid",
        customer_name=request.form.get("customer_name"),
        customer_phone=request.form.get("customer_phone")
    )

    db.session.add(booking)
    db.session.commit()

    flash("🎉 Đặt vé thành công!", "success")
    return redirect(url_for("booking_success", booking_id=booking.id))

@app.route('/booking-success/<int:booking_id>')
def booking_success(booking_id):  # Tên này phải khớp với url_for ở trên
    booking = Booking.query.get_or_404(booking_id)
    return render_template('booking_success.html', booking=booking)

@app.route("/qr/<code>")
def generate_ticket_qr(code): # Đổi tên ở đây
    img = qrcode.make(code)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

# QUẢN TRỊ (ADMIN) 

@app.route('/admin/users')
def admin_users():
    # Logic hiển thị danh sách người dùng
    return render_template('admin/users.html')

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    # 1. Tổng doanh thu tất cả các thời điểm
    total_revenue = db.session.query(func.sum(Booking.total_price)).filter_by(payment_status="Paid").scalar() or 0
    
    # 2. Thống kê doanh thu theo từng bộ phim
    revenue_by_movie = db.session.query(
        Movie.title, 
        func.sum(Booking.total_price).label('total')
    ).join(ShowtimeDB, Booking.showtime_id == ShowtimeDB.id) \
     .join(Movie, ShowtimeDB.movie_id == Movie.id) \
     .filter(Booking.payment_status == "Paid") \
     .group_by(Movie.title).all()

    # 3. Thống kê theo rạp chiếu
    revenue_by_theater = db.session.query(
        ShowtimeDB.theater, 
        func.sum(Booking.total_price).label('total')
    ).join(Booking, Booking.showtime_id == ShowtimeDB.id) \
     .filter(Booking.payment_status == "Paid") \
     .group_by(ShowtimeDB.theater).all()

    # Thêm các biến đếm cho thẻ thống kê
    total_bookings = Booking.query.count()
    total_users = User.query.count()
    total_movies = Movie.query.count()

    return render_template(
        "admin/dashboard.html", 
        revenue=total_revenue, # Đổi tên cho khớp với dashboard.html
        total_bookings=total_bookings,
        total_users=total_users,
        total_movies=total_movies,
        revenue_by_movie=revenue_by_movie,
        revenue_by_theater=revenue_by_theater
    )
@app.route("/admin/showtimes")
@admin_required
def admin_showtimes():
    if request.method == "POST":
        new_st = ShowtimeDB(
            movie_id=request.form["movie_id"],
            show_date=datetime.strptime(request.form["show_date"], "%Y-%m-%d").date(),
            show_time=datetime.strptime(request.form["show_time"], "%H:%M").time(),
            theater=request.form["theater"],
            price=int(request.form["price"])
        )
        db.session.add(new_st)
        db.session.commit()
        flash("Thêm suất chiếu thành công!", "success")
        # SỬA TẠI ĐÂY: Tên hàm phải là 'showtimes'
        return redirect(url_for("showtimes"))
    
    showtimes = ShowtimeDB.query.all()
    return render_template("admin/showtimes.html", showtimes=showtimes)

@app.route("/admin/showtimes/edit/<int:showtime_id>", methods=["GET", "POST"])
def edit_showtime(showtime_id):
    # Lấy lịch chiếu từ Database, nếu không thấy sẽ hiện lỗi 404
    st = ShowtimeDB.query.get_or_404(showtime_id)
    # Lấy danh sách phim để đổ vào dropdown (nếu cần đổi phim cho lịch chiếu)
    movies = MovieDB.query.all() 

    if request.method == "POST":
        # Cập nhật thông tin từ form gửi lên
        st.movie_id = request.form.get("movie_id")
        st.room = request.form.get("room")
        st.price = float(request.form.get("price"))
        
        # Xử lý định dạng ngày và giờ
        st.show_date = datetime.strptime(request.form.get("show_date"), '%Y-%m-%d')
        st.show_time = datetime.strptime(request.form.get("show_time"), '%H:%M').time()

        db.session.commit()
        flash("Cập nhật lịch chiếu thành công!", "success")
        return redirect(url_for("admin_showtimes"))

    return render_template("admin/edit_showtime.html", st=st, movies=movies)

@app.route("/admin/showtimes/delete/<int:showtime_id>")
def delete_showtime(showtime_id):
    # Tìm lịch chiếu cần xóa
    st = ShowtimeDB.query.get_or_404(showtime_id)
    
    try:
        db.session.delete(st)
        db.session.commit()
        flash("Đã xóa lịch chiếu thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi khi xóa: {str(e)}", "danger")
        
    return redirect(url_for("admin_showtimes"))

@app.route("/admin/reports")
@admin_required
def admin_reports():
    total_tickets = Booking.query.count()
    total_customers = User.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter_by(payment_status="Paid").scalar() or 0

    # Sửa lỗi NameError: Đổi Showtime thành ShowtimeDB
    # Sửa lỗi InvalidRequestError: Thêm select_from và join rõ ràng qua các bảng
    best_movie_query = db.session.query(
        Movie.title, db.func.count(Booking.id).label('t_count')
    ).select_from(Movie).join(ShowtimeDB, Movie.id == ShowtimeDB.movie_id)\
     .join(Booking, ShowtimeDB.id == Booking.showtime_id)\
     .group_by(Movie.title).order_by(db.text('t_count DESC')).first()
    
    best_movie = best_movie_query[0] if best_movie_query else "N/A"

    # Cập nhật dữ liệu bảng báo cáo chi tiết
    report_data = db.session.query(
        Movie.title.label('movie_title'),
        db.func.count(Booking.id).label('total_tickets'),
        db.func.sum(Booking.total_price).label('revenue')
    ).select_from(Movie).join(ShowtimeDB, Movie.id == ShowtimeDB.movie_id)\
     .join(Booking, ShowtimeDB.id == Booking.showtime_id)\
     .filter(Booking.payment_status == "Paid")\
     .group_by(Movie.title).all()

    return render_template("admin/reports.html", 
                           total_tickets=total_tickets, 
                           total_revenue=total_revenue, 
                           best_movie=best_movie, 
                           total_customers=total_customers, 
                           report_by_movie=report_data)

@app.route("/admin/export/csv")
@admin_required
def export_csv():
    # Sử dụng db.func.date để trích xuất ngày từ created_at
    daily_revenue = db.session.query(
        db.func.date(Booking.created_at).label('day'),
        db.func.sum(Booking.total_price)
    ).filter(Booking.payment_status == "Paid") \
     .group_by('day').order_by(db.text('day DESC')).all()

    si = StringIO()
    # Thêm tham số encoding để tránh lỗi font tiếng Việt khi mở bằng Excel
    si.write('\ufeff') 
    cw = csv.writer(si)
    cw.writerow(['Ngày', 'Doanh thu (VNĐ)'])
    cw.writerows(daily_revenue)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=doanh_thu_cine.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output 

if __name__ == "__main__":
    create_super_admin()
    socketio.run(app, debug=True)
