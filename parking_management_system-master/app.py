from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(20))
    vip_status = db.Column(db.String(20))
    driver_age = db.Column(db.Integer)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    amount = db.Column(db.Integer, default=0)


app.secret_key = "dev-secret-key"

# -----------------------------
# Global Dashboard Stats
# -----------------------------
TOTAL_SLOTS = 120
occupied_slots = 0
total_vehicles = 0
total_revenue = 0
slot_counter = 1

# Store booking records
booking_history = []

# Dummy Admin Credentials
ADMIN_USER = "admin"
ADMIN_PASS = "Rosh@2002"

ADMIN_DETAILS = {
    "name": "Roshni S",
    "employee_id": "EMP-1023"
}



# -----------------------------
# Dashboard Route
# -----------------------------
@app.route("/")
def index():

    bookings = Booking.query.all()

    occupied = Booking.query.filter_by(exit_time=None).count()
    total_slots = 120
    available = total_slots - occupied
    revenue = sum(b.amount for b in bookings)

    return render_template(
        "index.html",
        occupied=occupied,
        available=available,
        total_slots=total_slots,
        revenue=revenue
    )



# -----------------------------
# Booking Route
# -----------------------------
@app.route("/book", methods=["POST"])
def book_slot():

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
    global booking_history
    return render_template("bookings.html", bookings=booking_history)

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

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

with app.app_context():
    db.create_all()

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
