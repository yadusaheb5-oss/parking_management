from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# -----------------------------
# Configurations
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "dev-secret-key"

db = SQLAlchemy(app)

# -----------------------------
# Parking Capacity Settings
# -----------------------------
DOWNTOWN_CAPACITY = 120
AIRPORT_CAPACITY = 80

# -----------------------------
# Parking Price Settings
# -----------------------------
PRICE_2_WHEELER = 20
PRICE_4_WHEELER = 50
VIP_EXTRA = 30


# -----------------------------
# Database Model
# -----------------------------
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(20))
    vip_status = db.Column(db.String(20))
    driver_age = db.Column(db.Integer)
    location = db.Column(db.String(50))
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    amount = db.Column(db.Integer, default=0)


# -----------------------------
# Admin Credentials
# -----------------------------
ADMIN_USER = "admin"
ADMIN_PASS = "Rosh@2002"

ADMIN_DETAILS = {
    "name": "Roshni S",
    "employee_id": "EMP-1023"
}


# -----------------------------
# Login Route
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")

        if user == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = ADMIN_DETAILS
            return redirect(url_for("index"))
        else:
            flash("Invalid Credentials!", "error")

    return render_template("login.html")


# -----------------------------
# Logout Route
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


# -----------------------------
# Dashboard Route
# -----------------------------
@app.route("/")
def index():

    if "admin" not in session:
        return redirect(url_for("login"))

    all_bookings = Booking.query.all()

    recent_bookings = Booking.query.order_by(
        Booking.booking_time.desc()
    ).limit(5).all()

    # Dashboard stats
    occupied = Booking.query.filter_by(exit_time=None).count()
    total_slots = DOWNTOWN_CAPACITY + AIRPORT_CAPACITY
    available = total_slots - occupied
    revenue = sum(b.amount for b in all_bookings)

    return render_template(
        "index.html",
        occupied=occupied,
        available=available,
        total_slots=total_slots,
        revenue=revenue,
        bookings=recent_bookings,
        admin=session["admin"]
    )


# -----------------------------
# Booking Route
# -----------------------------
@app.route("/book", methods=["POST"])
def book_slot():

    if "admin" not in session:
        return redirect(url_for("login"))

    reg_no = request.form.get("reg_no")
    vehicle_type = request.form.get("vehicle_type")
    vip_status = request.form.get("vip_status")
    driver_age = request.form.get("driver_age")

    if vehicle_type == "4-Wheeler":
        amount = PRICE_4_WHEELER
    else:
        amount = PRICE_2_WHEELER

    if vip_status == "VIP":
        amount += VIP_EXTRA

    new_booking = Booking(
        reg_no=reg_no,
        vehicle_type=vehicle_type,
        vip_status=vip_status,
        driver_age=driver_age,
        amount=amount
    )

    db.session.add(new_booking)
    db.session.commit()

    flash("Booking Successful!", "success")
    return redirect(url_for("index"))


# -----------------------------
# Exit Route
# -----------------------------
@app.route("/exit", methods=["POST"])
def exit_slot():

    if "admin" not in session:
        return redirect(url_for("login"))

    reg_no = request.form.get("exit_reg_no")
    booking = Booking.query.filter_by(reg_no=reg_no, exit_time=None).first()

    if booking:
        booking.exit_time = datetime.utcnow()
        db.session.commit()
        flash("Vehicle Exited Successfully!", "success")
    else:
        flash("Vehicle Not Found!", "error")

    return redirect(url_for("index"))


# -----------------------------
# Booking History
# -----------------------------
@app.route("/bookings")
def bookings():

    if "admin" not in session:
        return redirect(url_for("login"))

    all_bookings = Booking.query.all()
    return render_template("bookings.html", bookings=all_bookings)


# -----------------------------
# Settings Page
# -----------------------------
@app.route("/settings", methods=["GET", "POST"])
def settings():

    global DOWNTOWN_CAPACITY, AIRPORT_CAPACITY
    global PRICE_2_WHEELER, PRICE_4_WHEELER, VIP_EXTRA

    if request.method == "POST":

        DOWNTOWN_CAPACITY = int(request.form.get("downtown"))
        AIRPORT_CAPACITY = int(request.form.get("airport"))

        PRICE_2_WHEELER = int(request.form.get("price_2"))
        PRICE_4_WHEELER = int(request.form.get("price_4"))
        VIP_EXTRA = int(request.form.get("vip_extra"))

        flash("Settings updated successfully")

    return render_template(
        "settings.html",
        downtown=DOWNTOWN_CAPACITY,
        airport=AIRPORT_CAPACITY,
        price2=PRICE_2_WHEELER,
        price4=PRICE_4_WHEELER,
        vip=VIP_EXTRA
    )


# -----------------------------
# Booking Form Page
# -----------------------------
@app.route("/book-page")
def book_page():

    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template("book.html")


# -----------------------------
# Create Database
# -----------------------------
with app.app_context():
    db.create_all()


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
