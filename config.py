import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:741159@localhost/evento'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    