from datetime import datetime,date,timedelta
from flask import Flask, flash, redirect, request, session, url_for,render_template
from flask_login import login_user
from flask_sqlalchemy import SQLAlchemy
import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from db_models import User, Booking, db
from config import Config
from flask_migrate import Migrate
from sqlalchemy import func
import random



app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)



@app.route("/")
def home():
    return render_template("index.html")

@app.context_processor
def inject_user():
    return dict(user_name=session.get('user_name'), is_admin=session.get('is_admin'))


@app.route('/admin_dashboard')
def admin_dashboard():
    users = User.query.all()
    bookings = Booking.query.order_by(Booking.event_date.asc()).all()
    return render_template('admin_dashboard.html', users=users, bookings=bookings)
@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for("admin_dashboard"))

    results = Booking.query.join(User).filter(
        (User.name.ilike(f"%{query}%")) |
        (Booking.event_type.ilike(f"%{query}%"))
    ).all()

    return render_template("search_results.html", results=results, query=query)

@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    user = User.query.get(user_id)
    if user and not user.is_admin:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.")
    return redirect(url_for("admin_dashboard"))

@app.route("/completed_events")
def completed_events():
    events = Booking.query.filter_by(status="Completed").all()
    total_revenue = sum(event.quote_amount for event in events)
    return render_template("completed_events.html", events=events, total_revenue=total_revenue)

@app.route("/events_by_date", methods=["GET", "POST"])
def events_by_date():
    events = []
    selected_date = None

    if request.method == "POST":
        selected_date = request.form.get("event_date")
        if selected_date:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            events = Booking.query.filter_by(event_date=date_obj).all()

    return render_template("events_by_date.html", events=events, selected_date=selected_date)


@app.route("/admin/delete_event/<int:event_id>")
def delete_event(event_id):
    event = Booking.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted successfully.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/edit_booking/<int:booking_id>", methods=["GET", "POST"])
def edit_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if request.method == "POST":
        booking.event_type = request.form.get("event_type")
        booking.event_date = datetime.strptime(request.form.get("event_date"), "%Y-%m-%d").date()
        booking.package = request.form.get("package")
        booking.quote_amount = float(request.form.get("quote_amount"))
        booking.status = request.form.get("status")

        db.session.commit()
        flash("Booking updated successfully.")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_booking.html", booking=booking)



@app.route("/admin/complete_event/<int:event_id>")
def complete_event(event_id):
    event = Booking.query.get(event_id)
    if event:
        event.status = "Completed"
        db.session.commit()
        flash("Event marked as completed.")
    return redirect(url_for("admin_dashboard"))


@app.route('/get_quote', methods=['GET', 'POST'])
def get_quote():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Store email in session for login redirection
            session['login_email'] = email
            flash('Please log in to continue', 'info')
            return redirect(url_for('login'))
        else:
            # Store email in session for registration
            session['register_email'] = email
            return redirect(url_for('register'))
    
    return render_template('get_quote.html')

@app.route("/login_user", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Fetch user by email
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Store user info in session
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            flash("Login successful!", "success")

            # Redirect based on admin status
            if user.is_admin:
                return redirect(url_for("admin_dashboard"))  # Change 'dashboard' to your admin route
            else:
                return redirect(url_for("user_dashboard"))  # Change 'home' to your user route

        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login_user"))

    return render_template("login.html")

@app.route("/user_dashboard")
def user_dashboard():
    user_id = session.get("user_id")
    upcoming_bookings = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.event_date >= date.today(),
        Booking.status != 'Completed'
    ).order_by(Booking.event_date).all()

    return render_template("user_dashboard.html", bookings=upcoming_bookings)


@app.route('/signup_user', methods=['GET', 'POST'])
def signup_user():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "User with this email already exists."

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(name=name, email=email, phone=phone, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return f"User {name} signed up successfully! <a href='/'>Go to login</a>"

    return render_template('signup.html')  # For GET requests


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            # Forward to reset password form
            return redirect(url_for("reset_password", email=email))
        else:
            return render_template("forgot_password.html", message="User not found.")
    return render_template("forgot_password.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    email = request.args.get("email") or request.form.get("email")
    user = User.query.filter_by(email=email).first()

    if not user:
        return "Invalid user."

    if request.method == "POST":
        new_password = request.form.get("new_password")

        # ✅ Use hashing!
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return render_template("reset_password.html", message="Password updated successfully!", email=email)

    return render_template("reset_password.html", email=email)



@app.route('/booking', methods=['GET', 'POST'])
def booking():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("You must log in to book an event.")
        return redirect(url_for('login_user'))

    if request.method == 'POST':
        user_id = session['user_id']  

        event_type = request.form['event_type']
        event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d')
        package = request.form['package']
        quote_amount = float(request.form['quote_amount'])
        payment_option = request.form['payment_option']  # 'now' or 'later'

        new_booking = Booking(
            user_id=user_id,
            event_type=event_type,
            event_date=event_date,
            package=package,
            quote_amount=quote_amount
        )
        db.session.add(new_booking)
        db.session.commit()

        if payment_option == 'now':
            return redirect('/payment')  # Redirect to your payment page

        return "Booking submitted successfully! We will contact you soon."

    return render_template('booking.html', min_date=(date.today() + timedelta(days=1)).isoformat())

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session:
        flash("Please log in to proceed with payment.")
        return redirect(url_for('login_user'))

    # Get the most recent booking
    booking = Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.id.desc()).first()
    if not booking:
        flash("No booking found to process payment.")
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        payment_method = request.form.get('method', 'upi')

        # Mark as paid (you can create a field in your model if needed)
        booking.payment_status = "Yes"
        db.session.commit()

        # Store payment + booking details in session
        session['payment_details'] = {
            'transaction_id': transaction_id,
            'amount': booking.quote_amount,
            'payment_method': payment_method,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'event_type': booking.event_type,
            'event_date': booking.event_date.strftime('%Y-%m-%d'),
            'package': booking.package,
            'quote_amount': booking.quote_amount
        }

        return redirect(url_for('payment_success'))

    return render_template('payment.html', amount=booking.quote_amount)


@app.route('/payment_success')
def payment_success():
    details = session.pop('payment_details', None)
    user_name = session.get('user_name', 'User')

    if not details:
        flash("No payment found.")
        return redirect(url_for('user_dashboard'))

    return render_template('payment_success.html', details=details, user_name=user_name)


@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for('home'))  

      
if __name__== "__main__":
    app.run(debug=True)