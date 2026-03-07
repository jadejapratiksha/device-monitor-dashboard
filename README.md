
# Device Monitor Dashboard

## Technology Choice

**Language:** Python 3  
**GUI Framework:** Tkinter  
**Charting Library:** Matplotlib  

Python was chosen because it allows fast prototyping and clean code organization. Tkinter is a lightweight GUI toolkit that comes bundled with Python, making it easy to build desktop interfaces without additional dependencies. Matplotlib integrates well with Tkinter and provides powerful visualization capabilities for displaying sensor trends.

---

# Application Overview

The **Device Monitor Dashboard** is a desktop application that simulates device sensor data and displays it in a graphical user interface.

The application monitors three simulated sensors:

- Temperature (°C)
- Humidity (%)
- Pressure (hPa)

Sensor values are generated internally using mathematical functions and random noise to simulate real-world sensor behavior. The values update automatically every **1 second** and are visualized using a live updating chart.

---
## Device Monitor Dashboard

A Tkinter-based desktop dashboard that simulates IoT sensor data and visualizes it in real time.

### Dashboard Preview

![Dashboard Screenshot](assets/dashboard.png)

# Features

- Real-time simulated sensor data
- Live updating chart showing recent sensor values
- Start / Stop simulation control
- Reset button to clear sensor history
- Warning indicator when sensor values exceed threshold
- Adjustable temperature threshold slider
- Dropdown menu to select which sensor to display in the chart
- Clean separation between UI and data logic

---

# Project Architecture

The project is organized into separate modules to ensure clean separation of concerns.

```
device-monitor-dashboard
│
├── README.md
│
└── src
    ├── main.py
    ├── simulator.py
    ├── model.py
    └── ui.py
```

### Module Responsibilities

**main.py**  
Entry point of the application. Initializes the GUI and starts the Tkinter event loop.

**simulator.py**  
Generates simulated sensor values using sine functions and random noise.

**model.py**  
Handles application logic and data management:
- stores latest sensor readings
- maintains history buffers
- evaluates warning thresholds

**ui.py**  
Implements the graphical user interface:
- displays sensor values
- handles user interaction
- updates the chart
- communicates with the model

---

# Design Patterns Used

## MVC (Model–View–Controller)

The project loosely follows the MVC architecture.

**Model:** `model.py`  
Handles application data and business logic.

**View:** `ui.py`  
Displays the user interface and charts.

**Controller:** `main.py`  
Initializes and connects the model and UI.

---

## Observer Pattern (Conceptual)

The UI periodically observes the model using a timer.

Every second:

```
SensorSimulator → DeviceModel → UI refresh
```

The UI fetches new values from the model and updates the display and chart.

---

# Architecture Diagram

```
           +--------------------+
           |  SensorSimulator   |
           |   simulator.py     |
           +---------+----------+
                     |
                     v
               +-----------+
               | DeviceModel |
               |  model.py   |
               +------+------+
                      |
                      v
                +------------+
                | DashboardUI|
                |   ui.py    |
                +------+-----+
                       |
                       v
                  Tkinter GUI
```

Data Flow:

```
Simulator → Model → UI → User
```

---

# How to Run the Application

### Step 1 — Clone the repository

```
git clone <repository-url>
```

### Step 2 — Install dependencies

```
pip install matplotlib
```

Tkinter is included with standard Python installations.

### Step 3 — Run the application

```
python src/main.py
```

---

# Possible Future Improvements

- Export sensor data to CSV
- Add automated unit tests
- Implement dark mode theme
- Support multiple charts simultaneously
- Improve UI styling

---

# Author

Pratikshaba Jadeja  
Master's Student — Computer Engineering  
Arizona State University
