cd C:\python\venhanh

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
pip install flask-socketio


pip install qrcode pillow
python app.py

pip install flask flask-sqlalchemy flask-socketio

db.create_all()
python create_admin.py
rm cinema.db