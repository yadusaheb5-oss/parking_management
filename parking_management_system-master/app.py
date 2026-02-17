from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
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
ADMIN_PASS = "1234"

ADMIN_DETAILS = {
    "name": "Roshni Sharma",
    "employee_id": "EMP-1023"
}



# -----------------------------
# Dashboard Route
# -----------------------------
@app.route("/")
def index():
    if "admin" not in session:
        return redirect(url_for("login"))

    global TOTAL_SLOTS, occupied_slots, total_revenue, booking_history

    available_slots = TOTAL_SLOTS - occupied_slots

    return render_template(
        "index.html",
        total_slots=TOTAL_SLOTS,
        occupied=occupied_slots,
        available=available_slots,
        revenue=total_revenue,
        bookings=booking_history,
        admin=session["admin"]
    )



# -----------------------------
# Booking Route
# -----------------------------
@app.route("/book", methods=["POST"])
def book_slot():
    global occupied_slots, total_vehicles, TOTAL_SLOTS
    global booking_history, total_revenue, slot_counter

    reg_no = request.form.get("reg_no")
    driver_age = request.form.get("driver_age")
    vehicle_type = request.form.get("vehicle_type")
    vip_status = request.form.get("vip_status")

    if occupied_slots < TOTAL_SLOTS:

        booking_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        booking = {
            "slot": slot_counter,
            "reg_no": reg_no,
            "age": driver_age,
            "vehicle_type": vehicle_type,
            "vip_status": vip_status,
            "booking_time": booking_time,
            "exit_time": None
        }

        booking_history.append(booking)

        occupied_slots += 1
        total_vehicles += 1

        # Pricing logic
        if vehicle_type == "4 Wheeler":
            total_revenue += 40
        else:
            total_revenue += 20

        slot_counter += 1

        flash("Booking Successful!", "success")
    else:
        flash("Parking is Full!", "error")

    return redirect(url_for("index"))


# -----------------------------
# Exit Route
# -----------------------------
@app.route("/exit", methods=["POST"])
def exit_vehicle():
    global occupied_slots

    reg_no = request.form.get("exit_reg_no")

    for booking in booking_history:
        if booking["reg_no"] == reg_no and booking["exit_time"] is None:
            occupied_slots -= 1
            exit_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
            booking["exit_time"] = exit_time
            flash("Vehicle Released Successfully!", "success")
            return redirect(url_for("index"))

    flash("Vehicle Not Found or Already Released!", "error")
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


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
