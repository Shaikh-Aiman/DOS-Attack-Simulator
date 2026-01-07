# Prerequisites

<p align="center">
  <img src="https://github.com/user-attachments/assets/5e3181f7-bd64-4799-822d-63966c28595b" alt="REQ IMG 1"
       width="700">
</p>


This document explains the system, software, and library requirements needed to run the __DOS Attack Simulator__ successfully.
<br>

---

## Python Dependency File

The project uses a separate `requirements.txt` file for installing dependencies using `pip`.

__Ensure you have the following Python packages installed:__ <br>

- __threading –__ Enables concurrent execution of the server, attack simulation, and GUI updates without blocking the application.

- __time –__ Provides timing functions for rate limiting, request scheduling, and delay management.

- __signal –__ Handles system signals (like Ctrl + C) to allow graceful shutdown of the application.

- __sys –__ Provides access to system-level operations such as controlled program termination.

- __webbrowser –__ Opens the locally hosted Flask server in the default web browser from the GUI.

- __csv –__ Enables exporting persistent security logs into CSV format for reporting and analysis.

- __random –__ Generates randomized delays between requests to simulate realistic attack traffic patterns.

- __queue (Queue, Empty) –__ Provides thread-safe communication between background threads and the GUI.

- __datetime –__ Generates precise timestamps for logging request events in the database.

- __collections (defaultdict, deque) –__ Implements efficient per-IP request tracking using sliding window logic.

### GUI & Interface Libraries

- __tkinter –__ Builds the desktop graphical user interface for the SOC-style dashboard.

- __tkinter.ttk –__ Provides themed and modern widgets for a consistent dark UI design.

- __tkinter.messagebox –__ Displays alerts, warnings, and informational dialogs to users.

- __tkinter.scrolledtext –__ Displays real-time scrolling logs in the GUI.

- __tkinter.filedialog –__ Allows users to select file locations for exporting logs.

### Networking & System Monitoring

- __requests –__ Sends HTTP requests from the attack simulator to the local Flask server.

- __psutil –__ Collects real-time CPU and memory usage metrics for system monitoring.

### Database

- __sqlite3 –__ Stores persistent security event logs locally in a lightweight relational database.

### Web Server

- __flask –__ Implements the local web server and API endpoint used to test rate limiting and access control.

- __flask.request –__ Extracts request metadata such as source IP address and headers.

- __flask.jsonify –__ Returns structured JSON responses with appropriate HTTP status codes.

### Visualization

- __matplotlib –__ Generates real-time CPU and memory usage graphs embedded in the GUI.

- __FigureCanvasTkAgg –__ Integrates Matplotlib plots seamlessly into the Tkinter interface.
