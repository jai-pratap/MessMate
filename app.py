"""
MessMate — Smart Hostel & Mess Management System
Desktop application built with Python, CustomTkinter and SQLite.
Run: python app.py
"""
import os, sqlite3, uuid, csv
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import customtkinter as ctk
except ImportError:
    raise SystemExit("Please install requirements first: pip install -r requirements.txt")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "data", "messmate.db")
QR_DIR = os.path.join(APP_DIR, "data", "qr_codes")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F4F7FB"
WHITE = "#FFFFFF"
NAVY = "#14243A"
NAVY_2 = "#1C3452"
BLUE = "#316BCE"
BLUE_LIGHT = "#EAF1FF"
TEXT = "#182638"
MUTED = "#718096"
GREEN = "#16845B"
GREEN_LIGHT = "#E7F6EF"
ORANGE = "#B96B16"
ORANGE_LIGHT = "#FFF3E3"
RED = "#C44747"
BORDER = "#E5EAF1"

MEAL_SLOTS = {
    "Breakfast": ("07:00", "10:00"),
    "Lunch": ("12:00", "15:00"),
    "Evening Snacks": ("16:00", "18:00"),
    "Dinner": ("19:00", "22:00"),
}
DAILY_MEALS = 4

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, roll_no TEXT NOT NULL UNIQUE,
            room TEXT, department TEXT, qr_token TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS meal_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            meal TEXT NOT NULL, meal_date TEXT NOT NULL,
            scanned_at TEXT NOT NULL,
            UNIQUE(student_id, meal, meal_date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        CREATE TABLE IF NOT EXISTS complaints(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER, subject TEXT NOT NULL,
            details TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        count = con.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            demo = [
                ("Aarav Sharma", "MM001", "A-101", "CSE"),
                ("Priya Verma", "MM002", "A-102", "ECE"),
                ("Kabir Singh", "MM003", "B-204", "CSE"),
            ]
            for name, roll, room, dept in demo:
                con.execute("""INSERT INTO students(name,roll_no,room,department,qr_token,created_at)
                    VALUES(?,?,?,?,?,?)""",
                    (name, roll, room, dept, uuid.uuid4().hex, datetime.now().isoformat(timespec="seconds")))
        con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('admin_username','admin')")
        con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('admin_password','MessMate@123')")

def current_meal():
    now = datetime.now().strftime("%H:%M")
    for meal, (start, end) in MEAL_SLOTS.items():
        if start <= now <= end:
            return meal
    return None

def meal_counts():
    with db() as con:
        today = date.today().isoformat()
        students = con.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0]
        taken = con.execute("SELECT COUNT(*) FROM meal_logs WHERE meal_date=?", (today,)).fetchone()[0]
        return students, taken

def make_qr(token, roll):
    try:
        import qrcode
        img = qrcode.make(token)
        path = os.path.join(QR_DIR, f"{roll}.png")
        img.save(path)
        return path
    except ImportError:
        return None

class MessMateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MessMate | Hostel & Mess Management")
        self.geometry("1280x800")
        self.minsize(1080, 680)
        self.configure(fg_color=BG)
        self.active_page = "Overview"
        self.sidebar = ctk.CTkFrame(self, width=238, corner_radius=0, fg_color=NAVY)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.pack(side="right", fill="both", expand=True)
        self.build_sidebar()
        self.show_page("Overview")

    def build_sidebar(self):
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(28, 34))
        ctk.CTkLabel(brand, text="MM", width=42, height=42, corner_radius=12,
                     fg_color=BLUE, text_color=WHITE, font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        title = ctk.CTkFrame(brand, fg_color="transparent")
        title.pack(side="left", padx=11)
        ctk.CTkLabel(title, text="MessMate", text_color=WHITE,
                     font=ctk.CTkFont(size=19, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title, text="HOSTEL MANAGEMENT", text_color="#9FB0C7",
                     font=ctk.CTkFont(size=9, weight="bold")).pack(anchor="w", pady=(2,0))
        ctk.CTkLabel(self.sidebar, text="WORKSPACE", text_color="#8295AE",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=24, pady=(0,10))
        navs = [
            ("Overview", "▦"), ("Students", "♙"), ("QR Scanner", "▣"),
            ("Meal Records", "☷"), ("Complaints", "✉"), ("Reports", "▤")
        ]
        self.nav_buttons = {}
        for name, symbol in navs:
            btn = ctk.CTkButton(self.sidebar, text=f"   {symbol}     {name}", anchor="w",
                height=44, corner_radius=9, fg_color=BLUE if name == "Overview" else "transparent",
                hover_color=NAVY_2, text_color=WHITE, font=ctk.CTkFont(size=13, weight="bold" if name=="Overview" else "normal"),
                command=lambda n=name: self.show_page(n))
            btn.pack(fill="x", padx=13, pady=3)
            self.nav_buttons[name] = btn
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#30445F").pack(fill="x", padx=20, pady=24)
        ctk.CTkLabel(self.sidebar, text="SYSTEM STATUS", text_color="#8295AE",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=24)
        status = ctk.CTkFrame(self.sidebar, fg_color="#203B58", corner_radius=10)
        status.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(status, text="●  Database connected", text_color="#8BE0B5",
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=12, pady=12)
        profile = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile.pack(side="bottom", fill="x", padx=18, pady=22)
        ctk.CTkLabel(profile, text="AD", width=38, height=38, corner_radius=20,
                     fg_color="#34516F", text_color=WHITE, font=ctk.CTkFont(weight="bold")).pack(side="left")
        p = ctk.CTkFrame(profile, fg_color="transparent")
        p.pack(side="left", padx=10)
        ctk.CTkLabel(p, text="Administrator", text_color=WHITE,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(p, text="MessMate Admin", text_color="#9FB0C7",
                     font=ctk.CTkFont(size=10)).pack(anchor="w")

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def header(self, title, subtitle):
        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.pack(fill="x", padx=34, pady=(28, 20))
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text=title, text_color=TEXT,
                     font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(left, text=subtitle, text_color=MUTED,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(4,0))
        ctk.CTkLabel(top, text=datetime.now().strftime("%A, %d %B %Y"),
                     text_color=MUTED, font=ctk.CTkFont(size=11)).pack(side="right", pady=8)

    def show_page(self, page):
        self.active_page = page
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color=BLUE if name == page else "transparent",
                          font=ctk.CTkFont(size=13, weight="bold" if name == page else "normal"))
        self.clear_main()
        getattr(self, f"page_{page.lower().replace(' ', '_')}")()

    def card(self, parent, label, value, note, accent=BLUE):
        card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=14, border_width=1, border_color=BORDER)
        card.pack(side="left", fill="both", expand=True, padx=(0,12))
        ctk.CTkFrame(card, width=4, fg_color=accent, corner_radius=3).pack(side="left", fill="y", padx=(0,14), pady=16)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, pady=15)
        ctk.CTkLabel(body, text=label.upper(), text_color=MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(body, text=str(value), text_color=TEXT,
                     font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w", pady=3)
        ctk.CTkLabel(body, text=note, text_color=MUTED,
                     font=ctk.CTkFont(size=10)).pack(anchor="w")

    def page_overview(self):
        self.header("Overview", "Your mess operations at a glance.")
        total, taken = meal_counts()
        remaining = max(total * DAILY_MEALS - taken, 0)
        row = ctk.CTkFrame(self.main, fg_color="transparent")
        row.pack(fill="x", padx=34, pady=(0,18))
        self.card(row, "Active students", total, "Currently registered", BLUE)
        self.card(row, "Meals served today", taken, "Verified QR scans", GREEN)
        self.card(row, "Meals remaining", remaining, "Of today's allocated meals", ORANGE)
        with db() as con:
            logs = con.execute("""SELECT s.name,s.roll_no,m.meal,m.scanned_at
                FROM meal_logs m JOIN students s ON s.id=m.student_id
                WHERE m.meal_date=? ORDER BY m.id DESC LIMIT 8""", (date.today().isoformat(),)).fetchall()
            open_complaints = con.execute("SELECT COUNT(*) FROM complaints WHERE status='Open'").fetchone()[0]
        content = ctk.CTkFrame(self.main, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=34, pady=(0,24))
        left = ctk.CTkFrame(content, fg_color=WHITE, corner_radius=14, border_width=1, border_color=BORDER)
        left.pack(side="left", fill="both", expand=True, padx=(0,12))
        ctk.CTkLabel(left, text="Recent meal activity", text_color=TEXT,
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=20, pady=(18,12))
        self.make_table(left, ("Student","Roll No.","Meal","Time"),
                        [(r["name"],r["roll_no"],r["meal"],r["scanned_at"][11:16]) for r in logs],
                        height=10)
        right = ctk.CTkFrame(content, fg_color=WHITE, corner_radius=14, border_width=1, border_color=BORDER, width=250)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        ctk.CTkLabel(right, text="Quick actions", text_color=TEXT,
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=18, pady=(18,14))
        for label, cmd in [("+  Add student",lambda:self.show_page("Students")),
                           ("▣  Open QR scanner",lambda:self.show_page("QR Scanner")),
                           ("▤  View reports",lambda:self.show_page("Reports"))]:
            ctk.CTkButton(right,text=label,anchor="w",height=42,fg_color=BLUE_LIGHT,
                hover_color="#DCE8FF",text_color=BLUE,command=cmd).pack(fill="x",padx=16,pady=5)
        ctk.CTkFrame(right,height=1,fg_color=BORDER).pack(fill="x",padx=16,pady=18)
        ctk.CTkLabel(right,text="Needs attention",text_color=TEXT,
                     font=ctk.CTkFont(size=13,weight="bold")).pack(anchor="w",padx=18)
        ctk.CTkLabel(right,text=f"{open_complaints} open complaints",text_color=ORANGE,
                     font=ctk.CTkFont(size=12)).pack(anchor="w",padx=18,pady=(8,4))
        ctk.CTkLabel(right,text="Meal allowance: 4 per student/day",text_color=MUTED,
                     font=ctk.CTkFont(size=10),wraplength=210).pack(anchor="w",padx=18,pady=8)

    def make_table(self, parent, columns, rows, height=14):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=WHITE, foreground=TEXT, fieldbackground=WHITE,
                        rowheight=34, borderwidth=0, font=("Segoe UI",10))
        style.configure("Treeview.Heading", background="#F2F5FA", foreground="#526176",
                        relief="flat", font=("Segoe UI",9,"bold"))
        style.map("Treeview", background=[("selected","#E7EFFF")], foreground=[("selected",TEXT)])
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(fill="both", expand=True, padx=16, pady=(0,16))
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        for col in columns:
            tree.heading(col,text=col)
            tree.column(col,width=max(100, int(750/max(len(columns),1))), anchor="w")
        y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y.set)
        tree.pack(side="left",fill="both",expand=True)
        y.pack(side="right",fill="y")
        for row in rows:
            tree.insert("", "end", values=row)
        return tree

    def page_students(self):
        self.header("Student management", "Register residents and issue their unique QR identity.")
        toolbar = ctk.CTkFrame(self.main,fg_color="transparent")
        toolbar.pack(fill="x",padx=34,pady=(0,14))
        search = ctk.CTkEntry(toolbar,placeholder_text="Search by name or roll number...",width=300,height=38)
        search.pack(side="left")
        ctk.CTkButton(toolbar,text="+  Add student",height=38,command=self.add_student_dialog).pack(side="right")
        panel = ctk.CTkFrame(self.main,fg_color=WHITE,corner_radius=14,border_width=1,border_color=BORDER)
        panel.pack(fill="both",expand=True,padx=34,pady=(0,24))
        with db() as con:
            rows=con.execute("SELECT id,name,roll_no,room,department,status FROM students ORDER BY id DESC").fetchall()
        tree=self.make_table(panel,("ID","Student","Roll No.","Room","Department","Status"),
             [(r["id"],r["name"],r["roll_no"],r["room"] or "—",r["department"] or "—",r["status"]) for r in rows],height=16)
        def filter_rows(*_):
            term=search.get().lower()
            for item in tree.get_children(): tree.delete(item)
            for r in rows:
                if term in r["name"].lower() or term in r["roll_no"].lower():
                    tree.insert("","end",values=(r["id"],r["name"],r["roll_no"],r["room"] or "—",r["department"] or "—",r["status"]))
        search.bind("<KeyRelease>",filter_rows)
        def selected():
            sel=tree.selection()
            if not sel:
                messagebox.showinfo("Select student","Please select a student first."); return None
            return tree.item(sel[0],"values")
        actions=ctk.CTkFrame(panel,fg_color="transparent")
        actions.pack(fill="x",padx=18,pady=(0,16))
        def download_qr():
            v=selected()
            if not v:return
            with db() as con: r=con.execute("SELECT qr_token,roll_no FROM students WHERE id=?",(v[0],)).fetchone()
            path=make_qr(r["qr_token"],r["roll_no"])
            if path:
                dest=filedialog.asksaveasfilename(defaultextension=".png",initialfile=f"{r['roll_no']}_QR.png",filetypes=[("PNG image","*.png")])
                if dest:
                    import shutil; shutil.copy(path,dest); messagebox.showinfo("QR ready",f"QR code saved to:\n{dest}")
            else: messagebox.showerror("Missing library","Install qrcode[pil] from requirements.txt.")
        ctk.CTkButton(actions,text="Download selected QR",fg_color=BLUE_LIGHT,text_color=BLUE,hover_color="#DCE8FF",command=download_qr).pack(side="left")
        ctk.CTkButton(actions,text="Deactivate student",fg_color="#FCECEC",text_color=RED,hover_color="#F8DDDD",command=lambda:self.deactivate_student(selected(),tree)).pack(side="left",padx=8)

    def add_student_dialog(self):
        win=ctk.CTkToplevel(self); win.title("Add student"); win.geometry("430x500"); win.transient(self); win.grab_set()
        ctk.CTkLabel(win,text="Register a student",font=ctk.CTkFont(size=22,weight="bold")).pack(anchor="w",padx=26,pady=(24,4))
        ctk.CTkLabel(win,text="A unique QR identity will be generated automatically.",text_color=MUTED).pack(anchor="w",padx=26,pady=(0,18))
        fields={}
        for label in ["Full name","Roll number","Room number","Department"]:
            ctk.CTkLabel(win,text=label,text_color=TEXT).pack(anchor="w",padx=26,pady=(8,3))
            ent=ctk.CTkEntry(win,height=38); ent.pack(fill="x",padx=26); fields[label]=ent
        def save():
            name=fields["Full name"].get().strip(); roll=fields["Roll number"].get().strip()
            if not name or not roll:
                messagebox.showwarning("Required fields","Name and roll number are required.",parent=win);return
            try:
                with db() as con:
                    con.execute("""INSERT INTO students(name,roll_no,room,department,qr_token,created_at)
                        VALUES(?,?,?,?,?,?)""",(name,roll,fields["Room number"].get().strip(),fields["Department"].get().strip(),uuid.uuid4().hex,datetime.now().isoformat(timespec="seconds")))
                win.destroy(); self.show_page("Students")
                messagebox.showinfo("Student registered","Student added successfully. Download their QR from the Students page.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate roll number","This roll number is already registered.",parent=win)
        ctk.CTkButton(win,text="Save student",height=42,command=save).pack(fill="x",padx=26,pady=24)

    def deactivate_student(self, values, tree):
        if not values:return
        if messagebox.askyesno("Confirm","Deactivate this student? Existing records will be retained."):
            with db() as con: con.execute("UPDATE students SET status='Inactive' WHERE id=?",(values[0],))
            self.show_page("Students")

    def page_qr_scanner(self):
        self.header("QR scanner", "Scan student QR codes to record meal consumption automatically.")
        wrap=ctk.CTkFrame(self.main,fg_color="transparent")
        wrap.pack(fill="both",expand=True,padx=34,pady=(0,24))
        left=ctk.CTkFrame(wrap,fg_color=WHITE,corner_radius=14,border_width=1,border_color=BORDER)
        left.pack(side="left",fill="both",expand=True,padx=(0,14))
        right=ctk.CTkFrame(wrap,fg_color=WHITE,corner_radius=14,border_width=1,border_color=BORDER,width=300)
        right.pack(side="right",fill="y"); right.pack_propagate(False)
        ctk.CTkLabel(left,text="Scan student identity",font=ctk.CTkFont(size=17,weight="bold"),text_color=TEXT).pack(anchor="w",padx=22,pady=(22,5))
        ctk.CTkLabel(left,text="Use webcam scanner or enter the QR token for testing.",text_color=MUTED).pack(anchor="w",padx=22)
        self.scan_result=ctk.CTkLabel(left,text="Waiting for scan",height=100,fg_color="#F2F6FC",corner_radius=12,text_color=MUTED,font=ctk.CTkFont(size=18,weight="bold"))
        self.scan_result.pack(fill="x",padx=22,pady=22)
        entry=ctk.CTkEntry(left,placeholder_text="Enter QR token (manual test mode)",height=42)
        entry.pack(fill="x",padx=22,pady=(0,10))
        ctk.CTkButton(left,text="Verify QR token",height=40,command=lambda:self.process_scan(entry.get().strip())).pack(anchor="w",padx=22)
        ctk.CTkButton(left,text="Start webcam scanner",height=40,fg_color=GREEN,hover_color="#116C4A",command=self.start_camera).pack(anchor="w",padx=22,pady=10)
        ctk.CTkLabel(right,text="Meal schedule",font=ctk.CTkFont(size=16,weight="bold"),text_color=TEXT).pack(anchor="w",padx=20,pady=(22,14))
        for meal,(start,end) in MEAL_SLOTS.items():
            ctk.CTkFrame(right,height=1,fg_color=BORDER).pack(fill="x",padx=18,pady=7)
            ctk.CTkLabel(right,text=meal,text_color=TEXT,font=ctk.CTkFont(size=12,weight="bold")).pack(anchor="w",padx=20)
            ctk.CTkLabel(right,text=f"{start} – {end}",text_color=MUTED,font=ctk.CTkFont(size=11)).pack(anchor="w",padx=20,pady=(2,4))
        meal=current_meal()
        ctk.CTkLabel(right,text=f"Current slot: {meal or 'Outside meal hours'}",text_color=GREEN if meal else ORANGE,
                     font=ctk.CTkFont(size=12,weight="bold")).pack(anchor="w",padx=20,pady=16)
        ctk.CTkLabel(right,text="Allowance is fixed at 4 meals per student per day.",wraplength=250,text_color=MUTED).pack(anchor="w",padx=20)

    def process_scan(self, token):
        if not token:return
        meal=current_meal()
        if not meal:
            self.scan_result.configure(text="Outside meal hours",text_color=ORANGE,fg_color=ORANGE_LIGHT);return
        with db() as con:
            student=con.execute("SELECT * FROM students WHERE qr_token=? AND status='Active'",(token,)).fetchone()
            if not student:
                self.scan_result.configure(text="QR not recognised / student inactive",text_color=RED,fg_color="#FCECEC");return
            try:
                con.execute("INSERT INTO meal_logs(student_id,meal,meal_date,scanned_at) VALUES(?,?,?,?)",
                    (student["id"],meal,date.today().isoformat(),datetime.now().isoformat(timespec="seconds")))
                msg=f"✓  {student['name']}  |  {meal} recorded"
                self.scan_result.configure(text=msg,text_color=GREEN,fg_color=GREEN_LIGHT)
            except sqlite3.IntegrityError:
                self.scan_result.configure(text=f"Already recorded: {student['name']} — {meal}",text_color=ORANGE,fg_color=ORANGE_LIGHT)

    def start_camera(self):
        try: import cv2
        except ImportError:
            messagebox.showerror("Camera module missing","Install dependencies using: pip install -r requirements.txt");return
        cap=cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera unavailable","No webcam detected or camera permission denied.");return
        detector=cv2.QRCodeDetector()
        messagebox.showinfo("Scanner started","A camera window will open. Press Q to stop scanning.")
        found=False
        while True:
            ok,frame=cap.read()
            if not ok:break
            data,points,_=detector.detectAndDecode(frame)
            if points is not None:
                import numpy as np
                pts=points.astype(int).reshape(-1,2)
                for i in range(len(pts)):
                    cv2.line(frame,tuple(pts[i]),tuple(pts[(i+1)%len(pts)]),(40,190,100),3)
            cv2.putText(frame,"MessMate QR Scanner  |  Press Q to quit",(15,30),cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),2)
            cv2.imshow("MessMate - QR Scanner",frame)
            if data:
                self.process_scan(data); found=True
                cv2.waitKey(900)
            if cv2.waitKey(1)&0xFF==ord('q'):break
        cap.release();cv2.destroyAllWindows()

    def page_meal_records(self):
        self.header("Meal records", "Review verified meal scans and daily consumption.")
        bar=ctk.CTkFrame(self.main,fg_color="transparent");bar.pack(fill="x",padx=34,pady=(0,12))
        ctk.CTkLabel(bar,text=f"Date: {date.today().strftime('%d %b %Y')}",text_color=MUTED).pack(side="left")
        ctk.CTkButton(bar,text="Export CSV",command=self.export_meals).pack(side="right")
        panel=ctk.CTkFrame(self.main,fg_color=WHITE,corner_radius=14,border_width=1,border_color=BORDER)
        panel.pack(fill="both",expand=True,padx=34,pady=(0,24))
        with db() as con:
            rows=con.execute("""SELECT s.name,s.roll_no,s.room,m.meal,m.meal_date,m.scanned_at
                FROM meal_logs m JOIN students s ON s.id=m.student_id ORDER BY m.id DESC LIMIT 500""").fetchall()
        self.make_table(panel,("Student","Roll No.","Room","Meal","Date","Scanned at"),
            [(r["name"],r["roll_no"],r["room"] or "—",r["meal"],r["meal_date"],r["scanned_at"][11:19]) for r in rows],height=17)

    def export_meals(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV file","*.csv")],initialfile="messmate_meal_records.csv")
        if not path:return
        with db() as con: rows=con.execute("""SELECT s.name,s.roll_no,s.room,m.meal,m.meal_date,m.scanned_at
            FROM meal_logs m JOIN students s ON s.id=m.student_id ORDER BY m.id DESC""").fetchall()
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f);w.writerow(["Student","Roll No","Room","Meal","Date","Scanned At"])
            for r in rows:w.writerow(list(r))
        messagebox.showinfo("Export complete",f"Records exported to:\n{path}")

    def page_complaints(self):
        self.header("Complaints & feedback", "Track student concerns and update their resolution status.")
        ctk.CTkButton(self.main,text="+  Log complaint",command=self.add_complaint_dialog).pack(anchor="e",padx=34,pady=(0,12))
        panel=ctk.CTkFrame(self.main,fg_color=WHITE,corner_radius=14,border_width=1,border_color=BORDER)
        panel.pack(fill="both",expand=True,padx=34,pady=(0,24))
        with db() as con:
            rows=con.execute("""SELECT c.id,COALESCE(s.name,'Unknown'),c.subject,c.details,c.status,c.created_at
                FROM complaints c LEFT JOIN students s ON s.id=c.student_id ORDER BY c.id DESC""").fetchall()
        tree=self.make_table(panel,("ID","Student","Subject","Details","Status","Created"),
            [(r[0],r[1],r[2],r[3][:45],r[4],r[5][:10]) for r in rows],height=16)
        def resolve():
            sel=tree.selection()
            if not sel:messagebox.showinfo("Select complaint","Select a complaint first.");return
            cid=tree.item(sel[0],"values")[0]
            with db() as con:con.execute("UPDATE complaints SET status='Resolved' WHERE id=?",(cid,))
            self.show_page("Complaints")
        ctk.CTkButton(panel,text="Mark selected as resolved",fg_color=GREEN,hover_color="#116C4A",command=resolve).pack(anchor="e",padx=18,pady=(0,16))

    def add_complaint_dialog(self):
        with db() as con: students=con.execute("SELECT id,name,roll_no FROM students WHERE status='Active' ORDER BY name").fetchall()
        win=ctk.CTkToplevel(self);win.title("Log complaint");win.geometry("460x460");win.transient(self);win.grab_set()
        ctk.CTkLabel(win,text="New complaint",font=ctk.CTkFont(size=21,weight="bold")).pack(anchor="w",padx=24,pady=(22,14))
        ctk.CTkLabel(win,text="Student",text_color=TEXT).pack(anchor="w",padx=24)
        choices={f"{s['name']} ({s['roll_no']})":s["id"] for s in students}
        student=ctk.CTkOptionMenu(win,values=list(choices) or ["No students"]);student.pack(fill="x",padx=24,pady=(4,12))
        ctk.CTkLabel(win,text="Subject",text_color=TEXT).pack(anchor="w",padx=24)
        subject=ctk.CTkEntry(win,placeholder_text="e.g. Food quality",height=38);subject.pack(fill="x",padx=24,pady=(4,12))
        ctk.CTkLabel(win,text="Description",text_color=TEXT).pack(anchor="w",padx=24)
        details=ctk.CTkTextbox(win,height=100);details.pack(fill="x",padx=24,pady=(4,12))
        def save():
            if not subject.get().strip() or not details.get("1.0","end").strip():
                messagebox.showwarning("Required","Please enter subject and description.",parent=win);return
            sid=choices.get(student.get())
            with db() as con:con.execute("INSERT INTO complaints(student_id,subject,details,created_at) VALUES(?,?,?,?)",
                (sid,subject.get().strip(),details.get("1.0","end").strip(),datetime.now().isoformat(timespec="seconds")))
            win.destroy();self.show_page("Complaints")
        ctk.CTkButton(win,text="Submit complaint",height=40,command=save).pack(fill="x",padx=24,pady=14)

    def page_reports(self):
        self.header("Reports & analytics", "A consolidated view of meal utilisation and student participation.")
        with db() as con:
            total=con.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0]
            today=date.today().isoformat()
            taken=con.execute("SELECT COUNT(*) FROM meal_logs WHERE meal_date=?",(today,)).fetchone()[0]
            bymeal=con.execute("SELECT meal,COUNT(*) n FROM meal_logs WHERE meal_date=? GROUP BY meal",(today,)).fetchall()
            weekly=con.execute("""SELECT meal_date,COUNT(*) n FROM meal_logs
                WHERE meal_date>=date('now','-6 days') GROUP BY meal_date ORDER BY meal_date""").fetchall()
        row=ctk.CTkFrame(self.main,fg_color="transparent");row.pack(fill="x",padx=34,pady=(0,18))
        self.card(row,"Registered active students",total,"Current residents",BLUE)
        self.card(row,"Today's meals consumed",taken,"Across all four meal slots",GREEN)
        self.card(row,"Today's meal capacity",total*4,"4 meals per student",ORANGE)
        panel=ctk.CTkFrame(self.main,fg_color=WHITE,corner_radius=14,border_width=1,border_color=BORDER)
        panel.pack(fill="both",expand=True,padx=34,pady=(0,24))
        ctk.CTkLabel(panel,text="Today's meal distribution",text_color=TEXT,font=ctk.CTkFont(size=16,weight="bold")).pack(anchor="w",padx=22,pady=(20,10))
        lookup={r["meal"]:r["n"] for r in bymeal}
        for meal in MEAL_SLOTS:
            line=ctk.CTkFrame(panel,fg_color="transparent");line.pack(fill="x",padx=22,pady=9)
            ctk.CTkLabel(line,text=meal,width=150,anchor="w",text_color=TEXT).pack(side="left")
            n=lookup.get(meal,0)
            ctk.CTkProgressBar(line,height=10,progress_color=BLUE,fg_color="#E9EEF5").pack(side="left",fill="x",expand=True,padx=12)
            # Configure progress bar separately to avoid dependence on widget internals.
            for child in line.winfo_children():
                if isinstance(child,ctk.CTkProgressBar):child.set(n/max(total,1))
            ctk.CTkLabel(line,text=f"{n} / {total}",width=70,text_color=MUTED).pack(side="right")
        ctk.CTkLabel(panel,text="Daily capacity is calculated automatically as active students × 4. A scan is accepted only during its configured meal window.",text_color=MUTED,wraplength=800).pack(anchor="w",padx=22,pady=(20,10))
        ctk.CTkButton(panel,text="Export meal records",command=self.export_meals).pack(anchor="w",padx=22,pady=(4,20))

if __name__ == "__main__":
    init_db()
    app=MessMateApp()
    app.mainloop()
