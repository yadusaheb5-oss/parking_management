import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# -----------------------------
# Global Dashboard Stats
# -----------------------------
TOTAL_SLOTS = 120
occupied_slots = 74
total_vehicles = 50


# -----------------------------
# Dashboard Route
# -----------------------------
@app.route("/")
def index():
    global TOTAL_SLOTS, occupied_slots, total_vehicles

    available_slots = TOTAL_SLOTS - occupied_slots

    return render_template(
        "index.html",
        total_slots=TOTAL_SLOTS,
        occupied=occupied_slots,
        available=available_slots,
        total_vehicles=total_vehicles
    )


# -----------------------------
# Booking Route
# -----------------------------
@app.route("/book", methods=["POST"])
def book_slot():
    global occupied_slots, total_vehicles, TOTAL_SLOTS

    location = request.form.get("location")
    vehicle_type = request.form.get("vehicle_type")
    reg_no = request.form.get("reg_no")
    driver_age = request.form.get("driver_age")

    # If slots available → book
    if occupied_slots < TOTAL_SLOTS:
        occupied_slots += 1
        total_vehicles += 1
            return redirect(url_for("index"))


        print("New Booking:")
        print("Location:", location)
        print("Vehicle Type:", vehicle_type)
        print("Registration:", reg_no)
        print("Driver Age:", driver_age)
    else:
        print("Parking Full")

    return redirect(url_for("index"))


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



