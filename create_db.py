# create_db.py
import mysql.connector
from config import Config
from flask import Flask
from app import db  # uninitialized SQLAlchemy instance
from db_models import User, Booking  # models only

def initialize_database():
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Root333'
        )
        my_cursor = mydb.cursor()
        my_cursor.execute("CREATE DATABASE IF NOT EXISTS evento")
        
        print("Databases:")
        my_cursor.execute("SHOW DATABASES")
        for dbname in my_cursor:
            print(f"- {dbname[0]}")

        print("\nCreating tables via Flask-SQLAlchemy...")

        app = Flask(__name__)
        app.config.from_object(Config)

        db.init_app(app)  # ✅ FIX: bind db to app

        with app.app_context():
            db.create_all()
            print("Tables created successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'my_cursor' in locals():
            my_cursor.close()
        if 'mydb' in locals():
            mydb.close()

if __name__ == '__main__':
    initialize_database()

# In Python shell or a script


# with app.app_context():
#     db.drop_all()
#     db.create_all()


from werkzeug.security import generate_password_hash
from db_models import User,db  # or wherever your User model is defined
from app import app
with app.app_context():
    admin = User.query.filter_by(email="admin@example.com").first()
    if not admin:
        admin = User(
            name="Admin",
            email="admin@example.com",
            phone="1234567890",
            password_hash=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print(" Admin user created.")


