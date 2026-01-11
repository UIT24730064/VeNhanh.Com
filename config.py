class Config:
    # Cấu hình sử dụng SQLite cho bản demo
    SQLALCHEMY_DATABASE_URI = 'sqlite:///demo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'venhanh_secret_key'