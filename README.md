# DOS Attack Simulator

![dos](https://github.com/user-attachments/assets/9029b1fb-1610-403c-9561-2550be23bf74)


A **desktop-based cybersecurity simulation tool** built using **Python, Tkinter, and Flask** that demonstrates **Denial of Service (DoS) attack behavior**, **rate limiting**, and **basic defense mechanisms** in a controlled, educational environment.
This project visualizes how modern systems respond to high request rates using **HTTP status codes (200, 429, 403)** and **auto-blacklisting**, while providing **real-time monitoring**, **persistent forensic logs (SQLite)**, and **CSV export**.

<p align="center">
  <img src="![DOS1](https://github.com/user-attachments/assets/b1afe41f-7163-48b6-aa96-08df3f3de6f4)" alt="Demo GIF" width="700">
</p>



### Project Objectives:

- Simulate DoS/distributed request patterns using multiple source IPs.
- Demonstrate per-IP rate limiting, `429` responses and automatic `403` blacklisting.
- Provide a live, dark-themed SOC dashboard showing CPU/MEM, live logs, and counters for `200`, `429`, and `403`.
- Persist all events for forensic analysis in an on-disk SQLite DB `security_events.db`.
- Let users view, filter and export persistent logs (CSV) from within the GUI.

<img width="803" height="526" alt="image" src="https://github.com/user-attachments/assets/37f62e66-39b2-48f5-a7d3-69fa17e543fd" />




### Installation:
To run this project locally, follow these steps:

- __Clone the repository:__ <br>


         git clone https://github.com/Shaikh-Aiman/DOS-Attack-Simulator

- __Navigate to the project directory:__
cd DOS-Attack-Simulator
- __Ensure you have Python installed on your system.__
- __Install the required dependencies.__
- __Run the application:__
    `python main.py`

---

### Working:

- Launch `python main.py`. GUI starts. Server is __offline__ by default.
- Click __Start Server__ to spawn the Flask server in a background thread. GUI `Server Status` turns ONLINE.
- Use __Start Attack__ to spawn multiple simulated clients (each with a unique IP). Counters and live logs start updating.
- __Per-IP rate limiting__: each IP has a sliding time window; when requests exceed `MAX_REQUESTS` within `TIME_WINDOW`, server returns `429`. Repeat offenders (over `BLACKLIST_AFTER_429`) receive `403` for `BLACKLIST_TIME` seconds.
- All request events are written to `security_events.db`. Use __Event Logs__ tab to view, filter by status code, export to CSV, or clear persistent logs.
- Click __Stop Attack__ to stop traffic. Click __Stop Server__ to mark server offline (GUI flag); the Flask dev server thread remains a background thread (browser access is blocked by GUI when offline to avoid false positives).
- Close the app or press `Ctrl+C` in terminal — program performs graceful shutdown (stops simulator, cancels GUI timers and exits).

![DOS5](https://github.com/user-attachments/assets/378f6728-2e0a-4bd4-8a5f-ea9a8a47cc2d)


### Usage of Buttons:

__Dashboard tab — Server Control__

- __Start Server —__ starts Flask app in background thread and sets GUI `Server Status: ONLINE`. If already started, no action.
- __Stop Server —__ sets GUI `Server Status: OFFLINE` (simulates server unavailability for demos). Browser opening is blocked while OFFLINE.
- __Open Browser —__ opens `http://127.0.0.1:5050` only when GUI shows server ONLINE; otherwise shows a warning.

__Dashboard tab — Attack Control__

- __Start Attack —__ resets live counters/logs, then starts the attack simulator with configurable bot count & duration (defaults present in code). Counters (200/429/403) begin at 0 and update live.
- __Stop Attack —__ stops the traffic simulator.
- __Clear Live Logs —__ clears the live log textarea and resets live counters to zero (does not affect DB unless `Clear DB Logs` used).

__Counters__

- `200`, `429`, `403` counters show how many responses of each type have been observed for the current attack session. They are reset when an attack starts or when clearing live logs.

__Event Logs tab__

- __Filter Status Code:__ type a status code (e.g., `429`) and click `Search` to show only matching DB rows. Empty search shows all logs.
- __Export CSV:__ saves current DB contents to a CSV file for reporting.
- __Clear DB Logs:__ deletes all persistent logs from the SQLite DB (confirm via GUI). After clearing, the DB is empty until new events are logged.

![DOS3](https://github.com/user-attachments/assets/81190d63-a9d2-451f-b4cb-5884faa2b434)

### Configuration:

Open the top of `main.py` to tune:

- __TIME_WINDOW —__ sliding window seconds.
- __MAX_REQUESTS —__ allowed requests per IP per window before `429`.
- __BLACKLIST_AFTER_429 —__ how many `429` hits trigger `403`/blacklist.
- __BLACKLIST_TIME —__ blacklist duration in seconds.
- __SIM.start(bots=..., duration=...) —__ number of simulated IPs and attack duration
- __NOTE:__ For demos, lower `MAX_REQUESTS` and shorter `TIME_WINDOW` to see `429` and `403` quickly.



### Testing & Observability (Wireshark / Browser)

- Use the __Loopback Adapter (on Windows)__ to capture localhost traffic in Wireshark.
- Start capturing before starting traffic in the app. Use display filters:
- `tcp.port == 5050`
- `http.response.code == 429`
- `http.response.code == 403`
- In browser DevTools (Network tab) you can also confirm response codes when server is __ONLINE__.

### Conclusion

This project demonstrates a realistic, per-IP rate limiting defense chain, with a SOC-style UI for live monitoring and persistent forensic logging. It is designed to be clear, reproducible and examiner-friendly: counters and logs reset per attack to allow repeatable demonstrations and straightforward analysis.

### ⚠️ Disclaimer

- For __educational and authorized testing__ only.
- Do not run this tool against systems for which you do not have explicit permission. Misuse may violate local laws and acceptable use policies. </n>



![DOS4](https://github.com/user-attachments/assets/48f1f3d4-6c26-46fd-b046-e41a05b646c8)

