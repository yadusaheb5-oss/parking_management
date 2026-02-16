import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# -----------------------------
# Global Dashboard Stats
# -----------------------------
TOTAL_SLOTS = 120
occupied_slots = 74
total_vehicles = 50

booking_history = []
total_revenue = 0
slot_counter = 1



# -----------------------------
# Dashboard Route
# -----------------------------
@app.route("/")
def index():
    global TOTAL_SLOTS, occupied_slots, total_vehicles
    global total_revenue, booking_history

    available_slots = TOTAL_SLOTS - occupied_slots

    return render_template(
        "index.html",
        total_slots=TOTAL_SLOTS,
        occupied=occupied_slots,
        available=available_slots,
        total_vehicles=total_vehicles,
        revenue=total_revenue,
        booking_history=booking_history
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

    if occupied_slots < TOTAL_SLOTS:
        occupied_slots += 1
        total_vehicles += 1

        booking = {
            "slot": slot_counter,
            "reg_no": reg_no,
            "age": driver_age
        }

        booking_history.append(booking)

        total_revenue += 20   # ₹20 flat rate
        slot_counter += 1

        flash("Booking Successful!", "success")
    else:
        flash("Parking is Full!", "error")

    return redirect(url_for("index"))



@app.route("/exit", methods=["POST"])
def exit_vehicle():
    global occupied_slots, booking_history

    reg_no = request.form.get("exit_reg_no")

    for booking in booking_history:
        if booking["reg_no"] == reg_no:
            booking_history.remove(booking)
            occupied_slots -= 1
            flash("Vehicle Exited Successfully!", "success")
            break
    else:
        flash("Vehicle Not Found!", "error")

    return redirect(url_for("index"))



# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
