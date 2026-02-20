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
# Admin Credentials (LOGIN ONLY)
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
# Dashboard Route (PROTECTED)
# -----------------------------
@app.route("/")
def index():
    if "admin" not in session:
        return redirect(url_for("login"))

    all_bookings = Booking.query.all()

    recent_bookings = Booking.query.order_by(
        Booking.booking_time.desc()
    ).limit(5).all()

    occupied = Booking.query.filter_by(exit_time=None).count()
    total_slots = 120
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

    amount = 50 if vehicle_type == "4-Wheeler" else 20
    if vip_status == "VIP":
        amount += 30

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
# Booking History Page
# -----------------------------
@app.route("/bookings")
def bookings():
    if "admin" not in session:
        return redirect(url_for("login"))

    all_bookings = Booking.query.all()
    return render_template("bookings.html", bookings=all_bookings)


# -----------------------------
# Settings Route
# -----------------------------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "admin" not in session:
        return redirect(url_for("login"))

    admin = Admin.query.first()

    if request.method == "POST":
        new_name = request.form.get("name")
        new_password = request.form.get("password")

        if new_name:
            admin.name = new_name

        if new_password:
            admin.password = new_password

        db.session.commit()
        flash("Settings updated successfully!", "success")

    return render_template("settings.html", admin=admin)


# -----------------------------
# Create Database + Default Admin
# -----------------------------
 

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
