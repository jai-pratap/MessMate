"""
Smart Hostel & Mess Management System
Course : Computational Thinking and Programming (2026CSAE100)
Bennett University - School of CSET

Team   : Jai Pratap Singh, Rohit Sharma, Sameer Singh, Divyansh Taliyan

Uses only the Python standard library (no installation needed). Python 3.8+.
Concepts used: lists, loops, conditions, arithmetic, functions,
input handling, formatted output (+ simple JSON file saving).
"""

import json
import os

# Saved next to this program file, so it works the same in IDLE, VS Code or terminal.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hostel_data.json")
REVIEW_LIMIT = 75      # below this -> "Needs Review"
GOOD_LIMIT = 90        # 90 and above -> "Good"
REPEATED_COMPLAINTS = 2  # this many complaints or more -> "repeated"

COMPLAINT_CATEGORIES = [
    "Food Quality", "Hygiene/Cleanliness", "Water/Electricity",
    "Meal Timing", "Staff Behaviour", "Room/Hostel Facility", "Other",
]

# Data is stored in lists, as required by the project algorithm.
students = []     # each item: dict with name, enrollment, room, mess_status,
                  #            available, taken
complaints = []   # each item: dict with enrollment, category, details


# ----------------------------------------------------------------------
# Input helpers (input handling + validation)
# ----------------------------------------------------------------------
def ask_text(prompt):
    """Ask until the user types something non-empty."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  ! This field cannot be empty. Try again.")


def ask_int(prompt, minimum, maximum):
    """Ask until the user types a whole number within [minimum, maximum]."""
    while True:
        raw = input(prompt).strip()
        try:
            number = int(raw)
        except ValueError:
            print("  ! Please enter a whole number.")
            continue
        if number < minimum or number > maximum:
            print(f"  ! Enter a number between {minimum} and {maximum}.")
            continue
        return number


def find_student(enrollment):
    """Return the student record with this enrollment number, or None."""
    for s in students:
        if s["enrollment"].lower() == enrollment.lower():
            return s
    return None


# ----------------------------------------------------------------------
# Calculation functions
# ----------------------------------------------------------------------
def attendance_percent(taken, available):
    """Meals attended / total available meals * 100."""
    if available == 0:
        return 0.0
    return taken / available * 100


def get_status(percent):
    """Good 90-100, Moderate 75-89.99, Needs Review below 75."""
    if percent >= GOOD_LIMIT:
        return "Good"
    if percent >= REVIEW_LIMIT:
        return "Moderate"
    return "Needs Review"


def complaint_count(enrollment):
    """Number of complaints recorded for one student."""
    count = 0
    for c in complaints:
        if c["enrollment"].lower() == enrollment.lower():
            count += 1
    return count


def totals():
    """Return (total_available, total_taken, overall_percent)."""
    total_available = sum(s["available"] for s in students)
    total_taken = sum(s["taken"] for s in students)
    return total_available, total_taken, attendance_percent(total_taken, total_available)


def category_counts():
    """Return a dict {category: number of complaints}."""
    counts = {}
    for c in complaints:
        counts[c["category"]] = counts.get(c["category"], 0) + 1
    return counts


# ----------------------------------------------------------------------
# Data entry
# ----------------------------------------------------------------------
def add_one_student():
    print("\n--- Enter Student / Hostel Record ---")
    name = ask_text("Student name           : ")
    while True:
        enrollment = ask_text("Enrollment number      : ").upper()
        if find_student(enrollment):
            print("  ! A record with this enrollment number already exists.")
        else:
            break
    room = ask_text("Room number (e.g. A-101): ").upper()
    print("Mess status: 1) Active   2) Inactive")
    mess_status = "Active" if ask_int("Choose (1/2)          : ", 1, 2) == 1 else "Inactive"
    available = ask_int("Total available meals  : ", 1, 1000)
    taken = ask_int(f"Meals taken (0-{available})     : ", 0, available)
    students.append({
        "name": name, "enrollment": enrollment, "room": room,
        "mess_status": mess_status, "available": available, "taken": taken,
    })
    print(f"  OK: record for {name} saved.")


def add_many_students():
    n = ask_int("\nHow many student records do you want to enter? ", 1, 200)
    for i in range(1, n + 1):
        print(f"\n[Record {i} of {n}]")
        add_one_student()
        # optionally record complaints for this student right away
        last = students[-1]
        count = ask_int("Number of complaints for this student (0-10): ", 0, 10)
        for _ in range(count):
            add_complaint_for(last)


def choose_category():
    print("Complaint category:")
    for i, cat in enumerate(COMPLAINT_CATEGORIES, start=1):
        print(f"  {i}) {cat}")
    return COMPLAINT_CATEGORIES[ask_int("Choose category number: ", 1, len(COMPLAINT_CATEGORIES)) - 1]


def add_complaint_for(student):
    category = choose_category()
    details = input("Short details (optional): ").strip() or "-"
    complaints.append({"enrollment": student["enrollment"],
                       "category": category, "details": details})
    print(f"  OK: complaint recorded for {student['name']}.")


def add_complaint_menu():
    if not students:
        print("\n  ! No student records yet. Add students first.")
        return
    print("\n--- Record a Complaint ---")
    enrollment = ask_text("Enrollment number of student: ").upper()
    student = find_student(enrollment)
    if student is None:
        print("  ! No student with that enrollment number.")
        return
    add_complaint_for(student)


def update_meals():
    if not students:
        print("\n  ! No student records yet.")
        return
    print("\n--- Update Meal Attendance ---")
    student = find_student(ask_text("Enrollment number: ").upper())
    if student is None:
        print("  ! No student with that enrollment number.")
        return
    student["available"] = ask_int(f"New total available meals (now {student['available']}): ", 1, 1000)
    student["taken"] = ask_int(f"New meals taken, 0-{student['available']} (now {student['taken']}): ",
                               0, student["available"])
    print("  OK: attendance updated.")


def delete_student():
    if not students:
        print("\n  ! No student records yet.")
        return
    enrollment = ask_text("\nEnrollment number to delete: ").upper()
    student = find_student(enrollment)
    if student is None:
        print("  ! No student with that enrollment number.")
        return
    if input(f"Delete {student['name']} and their complaints? (y/n): ").strip().lower() == "y":
        students.remove(student)
        complaints[:] = [c for c in complaints if c["enrollment"].lower() != enrollment.lower()]
        print("  OK: record deleted.")
    else:
        print("  Cancelled.")


# ----------------------------------------------------------------------
# Display and analysis
# ----------------------------------------------------------------------
LINE = "=" * 96


def show_records():
    if not students:
        print("\n  ! No records to show.")
        return
    print("\n" + LINE)
    print(f"{'Name':<20}{'Enrollment':<14}{'Room':<8}{'Mess':<10}{'Avail':>6}{'Taken':>7}"
          f"{'Att %':>8}{'Compl':>7}  {'Status':<12}")
    print("-" * 96)
    for s in students:
        pct = attendance_percent(s["taken"], s["available"])
        print(f"{s['name']:<20}{s['enrollment']:<14}{s['room']:<8}{s['mess_status']:<10}"
              f"{s['available']:>6}{s['taken']:>7}{pct:>8.1f}{complaint_count(s['enrollment']):>7}"
              f"  {get_status(pct):<12}")
    print(LINE)


def show_complaints():
    print("\n--- Complaint Analysis ---")
    if not complaints:
        print("No complaints recorded.")
        return
    print(f"Total complaints: {len(complaints)}\n")
    print("By category:")
    counts = category_counts()
    for cat in COMPLAINT_CATEGORIES:
        if cat in counts:
            print(f"  {cat:<24}{counts[cat]:>3}  {'#' * counts[cat]}")
    print("\nAll complaints:")
    for i, c in enumerate(complaints, start=1):
        s = find_student(c["enrollment"])
        name = s["name"] if s else c["enrollment"]
        print(f"  {i}. {name:<20} [{c['category']}] {c['details']}")


def attention_list():
    """Records needing attention: low attendance or repeated complaints."""
    result = []
    for s in students:
        pct = attendance_percent(s["taken"], s["available"])
        reasons = []
        if pct < REVIEW_LIMIT:
            reasons.append(f"low attendance ({pct:.1f}%)")
        cc = complaint_count(s["enrollment"])
        if cc >= REPEATED_COMPLAINTS:
            reasons.append(f"repeated complaints ({cc})")
        if reasons:
            result.append((s, reasons))
    return result


def show_attention():
    print("\n--- Records Requiring Attention ---")
    items = attention_list()
    if not items:
        print("No record needs attention right now.")
        return
    for s, reasons in items:
        print(f"  * {s['name']} (Room {s['room']}): " + ", ".join(reasons))


def show_summary():
    print("\n" + LINE)
    print("HOSTEL & MESS MANAGEMENT SUMMARY".center(96))
    print(LINE)
    if not students:
        print("No records available. Add data or load sample data first.")
        return
    total_available, total_taken, overall = totals()
    status = get_status(overall)
    print(f"Total students recorded   : {len(students)}")
    print(f"Total available meals     : {total_available}")
    print(f"Total meals taken         : {total_taken}")
    print(f"Overall mess attendance   : {overall:.1f}%")
    print(f"Management status         : {status}")
    print(f"Total complaints          : {len(complaints)}")

    top_meals = max(s["taken"] for s in students)
    best = [s["name"] for s in students if s["taken"] == top_meals]
    top_c = max(complaint_count(s["enrollment"]) for s in students)
    if top_c > 0:
        worst = [f"{s['name']} ({top_c})" for s in students
                 if complaint_count(s["enrollment"]) == top_c]
        print(f"Highest complaint count   : {', '.join(worst)}")
    else:
        print("Highest complaint count   : None (no complaints)")
    print(f"Highest meal participation: {', '.join(best)} ({top_meals} meals)")

    meaning = {
        "Good": "regular participation; continue the current routine.",
        "Moderate": "some variation; monitor participation.",
        "Needs Review": "attendance is low and may require attention.",
    }[status]
    print("\nInterpretation: Overall attendance is " + f"{overall:.1f}%, which is in the "
          f"{status.lower()} range - {meaning}")

    print("\nRecords requiring attention:")
    items = attention_list()
    if items:
        for s, reasons in items:
            print(f"  * {s['name']} (Room {s['room']}): " + ", ".join(reasons))
    else:
        print("  None.")
    print(LINE)


# ----------------------------------------------------------------------
# Sample data and file saving
# ----------------------------------------------------------------------
def load_sample():
    """Loads the exact sample data given in the project report."""
    if students:
        answer = input("  This will REPLACE all current records. Continue? (y/n): ").strip().lower()
        if answer != "y":
            print("  Cancelled. Your records are unchanged.")
            return
    students.clear()
    complaints.clear()
    sample = [
        ("Jai Pratap Singh", "S26CSEU1969", "A-101", 30, 27),
        ("Rohit Sharma", "S26CSE1964", "A-102", 30, 24),
        ("Sameer Singh", "S26CSE1971", "A-103", 30, 28),
        ("Divyansh Taliyan", "S26CSE1960", "A-104", 30, 26),
    ]
    for name, enr, room, avail, taken in sample:
        students.append({"name": name, "enrollment": enr, "room": room,
                         "mess_status": "Active", "available": avail, "taken": taken})
    complaints.extend([
        {"enrollment": "S26CSEU1969", "category": "Food Quality", "details": "Dal was cold"},
        {"enrollment": "S26CSE1964", "category": "Hygiene/Cleanliness", "details": "Dirty plates"},
        {"enrollment": "S26CSE1964", "category": "Meal Timing", "details": "Dinner served late"},
        {"enrollment": "S26CSE1960", "category": "Water/Electricity", "details": "No drinking water"},
    ])
    print("  OK: sample data from the project report loaded (4 students, 4 complaints).")


def save_data(quiet=False):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"students": students, "complaints": complaints}, f, indent=2)
        if not quiet:
            print(f"  OK: data saved to {DATA_FILE}")
    except OSError as err:
        print(f"  ! Could not save file: {err}")


def load_data(quiet=False):
    if not os.path.exists(DATA_FILE):
        if not quiet:
            print("  ! No saved file found. Save data first.")
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        students[:] = data["students"]
        complaints[:] = data["complaints"]
        if not quiet:
            print(f"  OK: loaded {len(students)} students and {len(complaints)} complaints.")
    except (OSError, ValueError, KeyError):
        print("  ! Saved file is damaged or unreadable.")


# ----------------------------------------------------------------------
# Main menu
# ----------------------------------------------------------------------
MENU = """
==================== SMART HOSTEL & MESS MANAGEMENT SYSTEM ====================
  1. Load sample data (from project report)  [replaces records]
  2. Enter multiple student records (with complaints)
  3. Add a single student record
  4. Record a complaint
  5. Update meal attendance of a student
  6. View all records
  7. Complaint analysis
  8. Records requiring attention
  9. Generate management summary
 10. Delete a student record
 11. Save data now (also saved automatically)
 12. Reload data from file
  0. Exit
==============================================================================="""


def main():
    actions = {
        1: load_sample, 2: add_many_students, 3: add_one_student,
        4: add_complaint_menu, 5: update_meals, 6: show_records,
        7: show_complaints, 8: show_attention, 9: show_summary,
        10: delete_student, 11: save_data, 12: load_data,
    }
    changing = {1, 2, 3, 4, 5, 10}   # menu options that change the data
    load_data(quiet=True)             # automatic load at start
    print("Welcome! Smart Hostel & Mess Management System")
    print(f"Loaded {len(students)} saved student record(s) and {len(complaints)} complaint(s).")
    while True:
        print(MENU)
        choice = ask_int("Enter your choice (0-12): ", 0, 12)
        if choice == 0:
            save_data(quiet=True)
            print("All records saved. Thank you for using the system. Goodbye!")
            break
        actions[choice]()
        if choice in changing:
            save_data(quiet=True)     # automatic save after every change
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped. Goodbye!")
