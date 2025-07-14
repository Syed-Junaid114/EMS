from datetime import datetime
#from app import db
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256))
    # Relationship to bookings
    bookings = db.relationship('Booking', backref='client', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Booking(db.Model):
    __tablename__ = 'booking'  # Match your existing table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_type = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    package = db.Column(db.String(100), nullable=False)
    quote_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pending')
    payment_status = db.Column(db.String(10), default="No")  # values: 'Yes' or 'No'
