**GIỚI THIỆU**
Vé Nhanh là hệ thống đặt vé xem phim trực tuyến cho phép người dùng:
- Xem danh sách phim đang chiếu / sắp chiếu
- Chọn suất chiếu, chọn ghế theo thời gian thực
- Thanh toán và nhận vé QR Code
- Quản trị phim, suất chiếu, người dùng và doanh thu qua dashboard admin
  
**CÔNG NGHỆ SỬ DỤNG**
- Backend: Python 3.8+, Flask
- Frontend: HTML5, Bootstrap 5, JavaScript
- Database: SQLite / MySQL
- Realtime: Flask-SocketIO
- Auth: Flask-Login
- QR Code: qrcode, Pillow

# HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY DỰ ÁN

## Cài Đặt
- Cài Python 3.8+
  Cài đặt môi trường và thư viện
1 nhắn tổ hợp Window + R -> cmd
2 cd C:\python\venhanh (chọn đúng đường dẫn lưu file sau khi tải xuống hoàn tất)
3 python -m venv .venv : Tạo môi trường giả lập
4 .venv\Scripts\activate : Khởi động môi trưởng giả lập
5 pip install -r requirements.txt : nhập tiếp câu lệch khởi tạo thư viện
6 pip install qrcode pillow : Khởi tạo QR
7 python app.py: web khởi chạy trên môi trường giả lập
  sẽ tạo tự động user admin
  User: admin
  Pass: admin123
  truy cập http://127.0.0.1:5000
  
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
venhanh/
│
├── app.py
├── config.py
├── requirements.txt
├── models.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── movie.html
│   ├── showtime.html
│   ├── seats.html
│   ├── confirmation.html
│   ├── booking_success.html
│   ├── my_tickets.html
│   ├── profile.html
│   ├── rap_phim.html
│   ├── khuyen_mai.html
│   │
│   └── admin/
│       ├── admin_base.html
│       ├── dashboard.html
│       ├── movies.html
│       ├── showtimes.html
│       ├── seats.html
│       ├── users.html
│       └── reports.html
│
└── README.md
