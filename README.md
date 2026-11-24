# MessMate — Desktop Edition

A professional-looking desktop hostel and mess management system built with Python.

## Features
- Dashboard with active-student, meals-served and remaining-meal statistics
- Student registration, search, activation status and unique QR code generation
- Webcam QR scanning with OpenCV
- Automatic meal-slot detection
- Four fixed daily meal entitlements per active student
- Duplicate scan prevention for the same student, meal and date
- Meal history with CSV export
- Complaint logging and resolution
- Meal utilisation reports
- SQLite database created automatically

## Requirements
- Python 3.10 or newer
- A webcam for live QR scanning (optional; token entry is available for testing)

## Run on Windows / macOS / Linux

1. Download and extract the project.
2. Open a terminal in the extracted `MessMate_Desktop` folder.
3. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   ```
4. Activate it:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Start the application:
   ```bash
   python app.py
   ```

## Demo login note
This desktop prototype opens directly into the admin workspace. The previous web prototype's demo credentials are not used in this desktop version. Add authentication before using it with real student data.

## Meal timings
Edit `MEAL_SLOTS` near the top of `app.py` to match the institution's actual schedule:
- Breakfast: 07:00–10:00
- Lunch: 12:00–15:00
- Evening Snacks: 16:00–18:00
- Dinner: 19:00–22:00

## QR workflow
1. Register a student in **Students**.
2. Select the student and choose **Download selected QR**.
3. The QR contains a unique random token, not the student's personal details.
4. Scan it from **QR Scanner** using the webcam.
5. The system determines the current meal slot and records one scan per student per meal per day.

## Important project notes
- The four meals are fixed by the system; there is no field for manually entering a meal allowance.
- The system records meal consumption, not a manually entered count.
- A duplicate scan for the same meal and date is rejected by a database uniqueness constraint.
- The default demo records are sample data. Replace them with real authorised records before a live pilot.
- The prototype stores data locally in `data/messmate.db`. Back up this file regularly.
- This is a college demonstration prototype, not a production-secured deployment. Add role-based authentication, audit logs, database backups and privacy controls before real-world use.

## GitHub
Create a new GitHub repository, upload the extracted project files, and commit them. Do not upload real student personal data or the generated database file.
