import threading
import time
import signal
import sys
import webbrowser
import csv
import random
from queue import Queue, Empty
from datetime import datetime
from collections import defaultdict, deque
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import psutil
import sqlite3
from flask import Flask, request, jsonify
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

HOST = "127.0.0.1"
PORT = 5050
BASE_URL = f"http://{HOST}:{PORT}"

TIME_WINDOW = 10
MAX_REQUESTS = 3        
BLACKLIST_AFTER_429 = 2
BLACKLIST_TIME = 60

DB_FILE = "security_events.db"

BG = "#0b1220"
FG = "#e5e7eb"
ACCENT = "#38bdf8"
WARN = "#fbbf24"
GOOD = "#4ade80"
BAD = "#f87171"

db = sqlite3.connect(DB_FILE, check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS logs (
    ts TEXT,
    ip TEXT,
    path TEXT,
    status INTEGER,
    note TEXT
)
""")
db.commit()
db_lock = threading.Lock()

def log_db(ts, ip, path, status, note):
    with db_lock:
        db.execute(
            "INSERT INTO logs VALUES (?,?,?,?,?)",
            (ts, ip, path, status, note)
        )
        db.commit()

def fetch_logs():
    with db_lock:
        return db.execute(
            "SELECT ts, ip, path, status, note FROM logs ORDER BY ts DESC"
        ).fetchall()

def clear_logs():
    with db_lock:
        db.execute("DELETE FROM logs")
        db.commit()

app = Flask(__name__)
req_map = defaultdict(deque)
rate_hits = defaultdict(int)
blacklist = {}
lock = threading.Lock()

@app.route("/", methods=["GET"])
def home():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    now = time.time()

    with lock:
        if ip in blacklist and now < blacklist[ip]:
            log_db(datetime.now().isoformat(), ip, "/", 403, "Firewall Block")
            return jsonify({"error": "Blocked"}), 403

        dq = req_map[ip]
        while dq and dq[0] < now - TIME_WINDOW:
            dq.popleft()
        dq.append(now)

        if len(dq) > MAX_REQUESTS:
            rate_hits[ip] += 1
            log_db(datetime.now().isoformat(), ip, "/", 429, "Rate Limit")
            if rate_hits[ip] >= BLACKLIST_AFTER_429:
                blacklist[ip] = now + BLACKLIST_TIME
                log_db(datetime.now().isoformat(), ip, "/", 403, "Auto Blacklist")
                return jsonify({"error": "Blacklisted"}), 403
            return jsonify({"error": "Too many requests"}), 429

    log_db(datetime.now().isoformat(), ip, "/", 200, "Allowed")
    return jsonify({"message": "OK"}), 200

def run_server():
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)

class TrafficSimulator:
    def __init__(self):
        self.running = False
        self.queue = Queue()

    def start(self, bots=5, duration=20):
        self.running = True
        for i in range(bots):
            ip = f"10.0.0.{i+1}"
            threading.Thread(
                target=self.worker,
                args=(ip, duration),
                daemon=True
            ).start()

    def worker(self, ip, duration):
        end = time.time() + duration
        while time.time() < end and self.running:
            try:
                r = requests.get(
                    BASE_URL,
                    headers={"X-Forwarded-For": ip},
                    timeout=2
                )
                self.queue.put((ip, r.status_code))
            except:
                self.queue.put((ip, "OFFLINE"))
            time.sleep(random.uniform(0.01, 0.03))

    def stop(self):
        self.running = False

SIM = TrafficSimulator()


class DOSSim:
    def __init__(self, root):
        self.root = root
        self.root.title("DOS Simulator")
        self.root.geometry("1300x860")
        self.root.configure(bg=BG)

        self.after_id = None
        self.server_online = False

        self.count_200 = 0
        self.count_429 = 0
        self.count_403 = 0

        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        signal.signal(signal.SIGINT, lambda *_: self.shutdown())

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Treeview",
                        background="#020617",
                        foreground=FG,
                        fieldbackground="#020617")

        nb = ttk.Notebook(root)
        nb.pack(fill=tk.BOTH, expand=True)

        self.tab_dash = ttk.Frame(nb)
        self.tab_db = ttk.Frame(nb)

        nb.add(self.tab_dash, text="Dashboard")
        nb.add(self.tab_db, text="Event Logs")

        self.build_dashboard()
        self.build_db_tab()

        self.after_id = self.root.after(1000, self.update)

    def build_dashboard(self):
        r = self.tab_dash

        ttk.Label(
            r,
            text="DOS Simulator",
            font=("Segoe UI", 18, "bold"),
            foreground=ACCENT
        ).pack(pady=10)

        ttk.Label(
            r,
            text="SERVER CONTROL",
            font=("Segoe UI", 12, "bold"),
            foreground=ACCENT
        ).pack(anchor="w", padx=15)

        server_bar = ttk.Frame(r)
        server_bar.pack(fill=tk.X, padx=15, pady=5)

        ttk.Button(server_bar, text="Start Server",
                   command=self.start_server).pack(side=tk.LEFT, padx=5)
        ttk.Button(server_bar, text="Stop Server",
                   command=self.stop_server).pack(side=tk.LEFT, padx=5)
        ttk.Button(server_bar, text="Open Browser",
                   command=self.open_browser_safe).pack(side=tk.LEFT, padx=5)

        self.server_status = ttk.Label(
            r,
            text="Server Status: OFFLINE",
            foreground=BAD,
            font=("Segoe UI", 11, "bold")
        )
        self.server_status.pack(anchor="w", padx=20)

        ttk.Label(
            r,
            text="ATTACK CONTROL",
            font=("Segoe UI", 12, "bold"),
            foreground=ACCENT
        ).pack(anchor="w", padx=15, pady=(15, 0))

        attack_bar = ttk.Frame(r)
        attack_bar.pack(fill=tk.X, padx=15, pady=5)

        ttk.Button(attack_bar, text="Start Attack",
                   command=self.start_attack).pack(side=tk.LEFT, padx=5)
        ttk.Button(attack_bar, text="Stop Attack",
                   command=SIM.stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(attack_bar, text="Clear Live Logs",
                   command=self.clear_live_logs).pack(side=tk.LEFT, padx=5)

        counter_bar = ttk.Frame(r)
        counter_bar.pack(fill=tk.X, padx=15, pady=10)

        self.lbl_200 = ttk.Label(counter_bar, text="200: 0", foreground=GOOD)
        self.lbl_429 = ttk.Label(counter_bar, text="429: 0", foreground=WARN)
        self.lbl_403 = ttk.Label(counter_bar, text="403: 0", foreground=BAD)

        self.lbl_200.pack(side=tk.LEFT, padx=20)
        self.lbl_429.pack(side=tk.LEFT, padx=20)
        self.lbl_403.pack(side=tk.LEFT, padx=20)

        ttk.Label(
            r,
            text="200 = Allowed   |   429 = Rate Limited   |   403 = Blocked",
            font=("Consolas", 10),
            foreground=WARN
        ).pack(pady=5)

        self.stats = ttk.Label(r, text="CPU: 0% | MEM: 0%")
        self.stats.pack()

        self.fig, self.ax = plt.subplots(figsize=(7, 3))
        self.cpu = deque(maxlen=60)
        self.mem = deque(maxlen=60)
        self.l1, = self.ax.plot([], [], label="CPU")
        self.l2, = self.ax.plot([], [], label="Memory")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, r)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.live_logs = scrolledtext.ScrolledText(
            r,
            bg="#020617",
            fg=FG,
            font=("Consolas", 10)
        )
        self.live_logs.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    def build_db_tab(self):
        r = self.tab_db

        top = ttk.Frame(r)
        top.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(top, text="Filter Status Code:").pack(side=tk.LEFT)
        self.search = ttk.Entry(top, width=10)
        self.search.pack(side=tk.LEFT, padx=5)

        ttk.Button(top, text="Search",
                   command=self.refresh_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Export CSV",
                   command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Clear DB Logs",
                   command=lambda: (clear_logs(), self.refresh_db())
                   ).pack(side=tk.LEFT, padx=5)

        cols = ("Time", "IP", "Path", "Status", "Note")
        self.tree = ttk.Treeview(r, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=240)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.refresh_db()

    def reset_counters(self):
        self.count_200 = self.count_429 = self.count_403 = 0
        self.update_counter_labels()

    def update_counter_labels(self):
        self.lbl_200.config(text=f"200: {self.count_200}")
        self.lbl_429.config(text=f"429: {self.count_429}")
        self.lbl_403.config(text=f"403: {self.count_403}")

    def start_server(self):
        if self.server_online:
            return
        threading.Thread(target=run_server, daemon=True).start()
        time.sleep(1)
        self.server_online = True
        self.server_status.config(
            text="Server Status: ONLINE",
            foreground=GOOD
        )

    def stop_server(self):
        self.server_online = False
        self.server_status.config(
            text="Server Status: OFFLINE",
            foreground=BAD
        )

    def open_browser_safe(self):
        if not self.server_online:
            messagebox.showwarning(
                "Server Offline",
                "Server is offline.\nStart the server first."
            )
            return
        webbrowser.open(BASE_URL)

    def start_attack(self):
        if not self.server_online:
            messagebox.showwarning("Server Offline", "Start server first.")
            return
        self.clear_live_logs()
        self.reset_counters()
        SIM.start(bots=5, duration=20)

    def clear_live_logs(self):
        self.live_logs.delete(1.0, tk.END)
        self.reset_counters()

    def refresh_db(self):
        code = self.search.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in fetch_logs():
            if code and str(row[3]) != code:
                continue
            self.tree.insert("", tk.END, values=row)

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "IP", "Path", "Status", "Note"])
            writer.writerows(fetch_logs())
        messagebox.showinfo("Exported", "CSV exported successfully")

    def update(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        self.stats.config(text=f"CPU: {cpu:.1f}% | MEM: {mem:.1f}%")

        self.cpu.append(cpu)
        self.mem.append(mem)
        self.l1.set_data(range(len(self.cpu)), self.cpu)
        self.l2.set_data(range(len(self.mem)), self.mem)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

        try:
            while True:
                ip, status = SIM.queue.get_nowait()
                self.live_logs.insert(tk.END, f"{ip} → {status}\n")
                self.live_logs.see(tk.END)

                if status == 200:
                    self.count_200 += 1
                elif status == 429:
                    self.count_429 += 1
                elif status == 403:
                    self.count_403 += 1

                self.update_counter_labels()
        except Empty:
            pass

        self.after_id = self.root.after(1000, self.update)

    def shutdown(self):
        SIM.stop()
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    DOSSim(root)
    root.mainloop()
