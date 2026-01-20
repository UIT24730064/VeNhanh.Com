# HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY DỰ ÁN

## Cài Đặt
- Cài Python 3.8+, MySQL Server.
- `pip install -r requirements.txt` (Flask, SQLAlchemy, SocketIO, etc.).
- Chạy `database.py` trong MySQL tạo DB `cinemadb` (tables movies/shows/seats/seatholds/tickets).
- Tạo `config.py`:
- Seed data phim/shows/seats từ database.py.
- `python app.py` (hoặc main.py nếu có), truy cập `http://localhost:5000`.

## Tính Năng Chính
- Quản lý phim (showing/upcoming), suất chiếu (theater, time, price).
- Chọn ghế real-time: available/holding/booked, hold 10 phút tự release.
- User auth (login/register), booking với QR code, profile, admin dashboard.
- Tích hợp promo: combo bắp giảm 20%, thứ Hai 45k, sinh viên 50k.
- Real-time updates qua Flask-SocketIO.

## Chạy & Sử Dụng
- Home: Danh sách phim poster (sử dụng images).
- Chọn suất → Seats page: Click hold ghế (vàng), tính tiền real-time.
- Booking: Tạo ticket, update status BOOKED.
- Admin: Quản lý shows, revenue query từ database.py.

## Cấu trúc thư mục dự án
project/
├── database.py # SQL schema + samples
├── models.py # Flask-SQLAlchemy ORM
├── seats.js # Frontend seat selection SocketIO
├── requirements.txt # Dependencies
├── static/images/ # Posters & promos
│ ├── cgv_q7.jpg
│ ├── cgv_thuduc.jpg
│ ├── nha-tran-quy.jpg
│ ├── nha-hai-chu.jpg
│ ├── con-ke-ba-nghe.jpg
│ ├── thien-duong-mau.jpg
│ ├── logo.jpg
│ ├── promo_combo.jpg
│ ├── promo_monday.jpg
│ └── promo_student.jpg
└── templates/ # HTML (seats.html dùng seats.js)

## Troubleshooting
- **No tables**: Chạy lại database.py.
- **Socket errors**: Cài eventlet, chạy với `eventlet.run()`.
- **MySQL connect**: Kiểm tra URI trong config.
- Thiếu app.py/main.py/routes: Dựa models tạo Flask app cơ bản với SocketIO.