# create_db.py
import mysql.connector
from config import Config  # Import your configuration
def initialize_database():
    try:
        # Connect to MySQL Server
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='741159'
        )
        
        my_cursor = mydb.cursor()
        
        # Create event database (matches your SQLALCHEMY_DATABASE_URI)
        my_cursor.execute("CREATE DATABASE IF NOT EXISTS evento")
        
        # Show databases for verification
        print("Databases:")
        my_cursor.execute("SHOW DATABASES")
        for db in my_cursor:
            print(f"- {db[0]}")
            
        print("\nCreating tables via Flask-SQLAlchemy...")
        
        # Initialize Flask app to create tables
        from app import create_app, db
        from db_models import Admin, User, Booking
        
        app = create_app(Config)
        with app.app_context():
            db.create_all()
            
    
        
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

from app import app
from db_models import db

# with app.app_context():
#     db.drop_all()
#     db.create_all()


# from werkzeug.security import generate_password_hash
# from db_models import User,db  # or wherever your User model is defined
# from app import app
# with app.app_context():
#     admin = User.query.filter_by(email="admin@example.com").first()
#     if not admin:
#         admin = User(
#             name="Admin",
#             email="admin@example.com",
#             phone="1234567890",
#             password_hash=generate_password_hash("admin123"),
#             is_admin=True
#         )
#         db.session.add(admin)
#         db.session.commit()
#         print(" Admin user created.")


