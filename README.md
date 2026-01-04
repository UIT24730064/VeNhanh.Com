HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY DỰ ÁN
================================

1. CHUẨN BỊ MÔI TRƯỜNG
- Cài đặt Python 3.8+ từ python.org
- Cài đặt MySQL Server từ mysql.com

2. CLONE/TẢI DỰ ÁN
Tải tất cả file Python (.py) và file SQL vào một thư mục

3. CÀI ĐẶT DEPENDENCIES
pip install -r requirements.txt

4. SETUP DATABASE
a) Mở MySQL Command Line Client hoặc MySQL Workbench
b) Chạy lệnh:
   mysql -u root -p < database.sql
c) Hoặc import file database.sql trong Workbench

5. CẤU HÌNH KẾT NỐI DATABASE
Mở file config.py và sửa:
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/movie_booking'

Thay:
- root = tên user MySQL
- password = mật khẩu MySQL
- localhost = server (mặc định localhost)
- movie_booking = tên database

6. CHẠY ỨNG DỤNG
python main.py

Truy cập: http://localhost:5000

7. TÀI KHOẢN MẶC ĐỊNH (NẾU CÓ SEED DATA)
Chưa có seed data, bạn cần tạo:
- Tạo tài khoản admin hoặc user thông qua /auth/register
- Thêm phim vào database hoặc qua admin panel

8. CẤU TRÚC THƯ MỤC DỰ ÁN
movie_booking/
├── main.py              # Entry point
├── config.py            # Cấu hình
├── models.py            # Database models
├── routes.py            # Routes/Controllers
├── services.py          # Business logic
├── auth.py              # Authentication
├── utils.py             # Helper functions
├── requirements.txt     # Dependencies
├── database.sql         # Schema
└── templates/           # HTML templates (cần tạo)
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── movies.html
    ├── showtime.html
    ├── seats.html
    └── booking_success.html

9. TẠMMOBILE TEMPLATES (NẾUT CẦN)
Bạn cần tạo các file HTML templates trong thư mục templates/
Các file này sử dụng Jinja2 template syntax

10. TROUBLESHOOTING
- Lỗi: "No module named 'flask'"
  Giải pháp: pip install -r requirements.txt

- Lỗi: "Can't connect to MySQL"
  Giải pháp: Kiểm tra MySQL service đang chạy, sửa config.py

- Lỗi: "table 'movie_booking.users' doesn't exist"
  Giải pháp: Chạy database.sql để tạo bảng

11. CÁC ROUTES CHÍNH

GET  /                           # Home page
GET  /auth/login                 # Login form
POST /auth/login                 # Process login
GET  /auth/register              # Register form
POST /auth/register              # Process register
GET  /auth/logout                # Logout
GET  /movie/movies               # List movies
GET  /movie/movie/<id>/showtimes # Movie showtimes
GET  /movie/showtime/<id>/seats  # Select seats
POST /movie/booking/create       # Create booking
GET  /movie/booking/<id>/success # Booking success
POST /movie/booking/<id>/cancel  # Cancel booking
GET  /profile                    # User profile
GET  /admin/dashboard            # Admin dashboard

12. NGUYÊN TẮC OOP TRONG CODE

✓ Encapsulation: User password hashing với @property
✓ Inheritance: BaseModel cho tất cả models
✓ Polymorphism: Service classes với static methods chung
✓ Composition: Booking chứa User, Showtime, Seats objects

13. MVC ARCHITECTURE

M - Models (models.py): Định nghĩa database structure
V - Views (templates/): HTML templates
C - Controllers (routes.py): Xử lý requests

Services (services.py): Business logic layer
Auth (auth.py): Authentication & authorization

14. MẠNH ĐỦ CHẠY TỰ DO

Tất cả code đã sẵn sàng để chạy!
Chỉ cần tạo templates và seed data là có thể sử dụng đầy đủ
