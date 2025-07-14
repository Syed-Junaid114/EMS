import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Root333@localhost/evento'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    