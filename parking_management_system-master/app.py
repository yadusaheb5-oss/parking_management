import io
import sys
import os
from flask import Flask, render_template, request, redirect, url_for, flash

from parking_management import ParkingManagement


app = Flask(__name__)
app.secret_key = "dev-secret-key"  # Replace for production


def run_commands_and_capture_output(commands_text):
    """
    Run the given parking system commands and capture printed output as a string.
    """
    buffer = io.StringIO()
    original_stdout = sys.stdout
    try:
        sys.stdout = buffer
        pm = ParkingManagement()
        for raw_line in commands_text.splitlines():
            line = raw_line.rstrip("\n\r")
            if not line:
                continue
            pm.parse_commands(line)
    finally:
        sys.stdout = original_stdout
    return buffer.getvalue()


# Global parking management instance for ticket generation
_pm_instance = None

def get_pm_instance():
    """Get or create a global parking management instance"""
    global _pm_instance
    if _pm_instance is None:
        _pm_instance = ParkingManagement()
        # Initialize with default capacity
        _pm_instance.create_parking_slots(100)
    return _pm_instance


@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    input_text = ""
    ticket_info = None
    locations = [
        {"id": "downtown", "name": "Downtown Garage", "capacity": 6},
        {"id": "airport", "name": "Airport Lot A", "capacity": 12},
        {"id": "mall", "name": "City Mall Parking", "capacity": 8},
    ]
    selected_location = request.form.get("location") if request.method == "POST" else locations[0]["id"]

    if request.method == "POST":
        # Check if this is a ticket generation request
        if request.form.get("action") == "generate_ticket":
            reg_no = request.form.get("ticket_reg_no", "").strip()
            driver_age = request.form.get("ticket_driver_age", "").strip()
            ticket_location = request.form.get("ticket_location", "")
            
            if not reg_no or not driver_age:
                flash("Please provide both registration number and driver age.", "error")
            else:
                try:
                    pm = get_pm_instance()
                    # Ensure location capacity is set
                    if ticket_location:
                        loc_info = next((l for l in locations if l["id"] == ticket_location), None)
                        if loc_info:
                            # Reinitialize if needed
                            if pm.capacity != loc_info["capacity"]:
                                pm = ParkingManagement()
                                pm.create_parking_slots(loc_info["capacity"])
                                _pm_instance = pm
                    
                    slot = pm.issue_parking_ticket(reg_no, int(driver_age))
                    if slot == -1:
                        flash("Parking lot is full. No slots available.", "error")
                    else:
                        # Get ticket details
                        ticket = pm.occupied_parking_slots.get(reg_no)
                        if ticket:
                            ticket_info = {
                                "slot": slot,
                                "reg_no": reg_no,
                                "driver_age": int(driver_age),
                                "location": next((l["name"] for l in locations if l["id"] == ticket_location), "Parking Lot")
                            }
                        else:
                            ticket_info = {
                                "slot": slot,
                                "reg_no": reg_no,
                                "driver_age": int(driver_age),
                                "location": next((l["name"] for l in locations if l["id"] == ticket_location), "Parking Lot")
                            }
                except Exception as e:
                    flash(f"Error generating ticket: {str(e)}", "error")
        else:
            # Original command execution flow
            # Option 1: textarea input
            input_text = request.form.get("commands", "")

            # Option 2: file upload (takes precedence if provided)
            uploaded_file = request.files.get("input_file")
            if uploaded_file and uploaded_file.filename:
                try:
                    input_text = uploaded_file.read().decode("utf-8")
                except Exception:
                    flash("Could not read uploaded file. Ensure it's UTF-8 text.", "error")
                    return redirect(url_for("index"))

            # If a location is selected, ensure the first command sets capacity for that location
            if selected_location:
                location_info = next((l for l in locations if l["id"] == selected_location), None)
                if location_info:
                    capacity_line = f"Create_parking_lot {location_info['capacity']}"
                    normalized = input_text.lstrip()
                    if not normalized.startswith("Create_parking_lot"):
                        input_text = capacity_line + ("\n" + input_text if input_text.strip() else "")

            if not input_text.strip():
                flash("Please provide commands or upload a file.", "error")
                return redirect(url_for("index"))

            output = run_commands_and_capture_output(input_text)

    return render_template("index.html", output=output, input_text=input_text, locations=locations, selected_location=selected_location, ticket_info=ticket_info)

@app.route("/book", methods=["POST"])
def book_slot():
    location = request.form.get("location")
    vehicle_type = request.form.get("vehicle_type")
    reg_no = request.form.get("reg_no")
    driver_age = request.form.get("driver_age")

    print("New Booking:")
    print(location, vehicle_type, reg_no, driver_age)

    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


