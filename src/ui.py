# ui.py
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from model import DeviceModel


class DashboardUI:
    def __init__(self, root: tk.Tk, model: DeviceModel) -> None:
        self.root = root
        self.model = model

        self.root.title("Device Monitor Dashboard")
        self.root.geometry("900x650")

        self.update_interval_ms = 1000

        # ---------------- Top Frame ----------------
        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        self.status_var = tk.StringVar(value="STOPPED")
        self.status_label = ttk.Label(top, textvariable=self.status_var)
        self.status_label.pack(side="left")

        self.start_stop_btn = ttk.Button(top, text="Start", command=self.toggle_start_stop)
        self.start_stop_btn.pack(side="left", padx=10)

        self.reset_btn = ttk.Button(top, text="Reset", command=self.reset_history)
        self.reset_btn.pack(side="left", padx=5)

        ttk.Label(top, text="Chart sensor:").pack(side="left", padx=(20, 5))
        self.chart_sensor_var = tk.StringVar(value="temperature")
        self.chart_sensor_dropdown = ttk.Combobox(
            top,
            textvariable=self.chart_sensor_var,
            values=["temperature", "humidity", "pressure"],
            state="readonly",
            width=12,
        )
        self.chart_sensor_dropdown.pack(side="left")
        self.chart_sensor_dropdown.bind("<<ComboboxSelected>>", lambda event: self.refresh_chart())

        # ---------------- Middle Frame ----------------
        mid = ttk.Frame(root, padding=10)
        mid.pack(fill="x")

        self.temp_var = tk.StringVar(value="Temp: -- °C")
        self.hum_var = tk.StringVar(value="Humidity: -- %")
        self.pres_var = tk.StringVar(value="Pressure: -- hPa")

        self.temp_label = ttk.Label(mid, textvariable=self.temp_var, font=("Segoe UI", 12))
        self.hum_label = ttk.Label(mid, textvariable=self.hum_var, font=("Segoe UI", 12))
        self.pres_label = ttk.Label(mid, textvariable=self.pres_var, font=("Segoe UI", 12))

        self.temp_label.pack(anchor="w", pady=4)
        self.hum_label.pack(anchor="w", pady=4)
        self.pres_label.pack(anchor="w", pady=4)

        # ---------------- Threshold Frame ----------------
        bottom = ttk.Frame(root, padding=10)
        bottom.pack(fill="x")

        ttk.Label(bottom, text="Temp warning threshold (°C):").pack(side="left")

        self.threshold_var = tk.DoubleVar(value=self.model.temp_threshold_c)
        self.threshold_slider = ttk.Scale(
            bottom,
            from_=15.0,
            to=35.0,
            orient="horizontal",
            variable=self.threshold_var,
            command=self.on_threshold_change,
            length=250,
        )
        self.threshold_slider.pack(side="left", padx=10)

        self.threshold_value_label = ttk.Label(bottom, text=f"{self.model.temp_threshold_c:.1f}")
        self.threshold_value_label.pack(side="left")

        # ---------------- Chart Frame ----------------
        chart_frame = ttk.Frame(root, padding=10)
        chart_frame.pack(fill="both", expand=True)

        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Sensor Trend")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Value")

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        self._after_id = None

        self.refresh_ui()
        self.refresh_chart()

    def on_threshold_change(self, _value: str) -> None:
        self.model.temp_threshold_c = float(self.threshold_var.get())
        self.threshold_value_label.config(text=f"{self.model.temp_threshold_c:.1f}")
        self.refresh_ui()

    def toggle_start_stop(self) -> None:
        if self.model.running:
            self.model.stop()
            self.status_var.set("STOPPED")
            self.start_stop_btn.config(text="Start")
            if self._after_id is not None:
                self.root.after_cancel(self._after_id)
                self._after_id = None
        else:
            self.model.start()
            self.status_var.set("RUNNING")
            self.start_stop_btn.config(text="Stop")
            self.schedule_next_update()

    def reset_history(self) -> None:
        self.model.stop()
        self.status_var.set("STOPPED")
        self.start_stop_btn.config(text="Start")

        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None

        self.model.reset_history()
        self.refresh_ui()
        self.refresh_chart()

    def schedule_next_update(self) -> None:
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)

        self._after_id = self.root.after(self.update_interval_ms, self.on_timer_tick)

    def on_timer_tick(self) -> None:
        if self.model.running:
            self.model.update_once()
            self.refresh_ui()
            self.refresh_chart()
            self.schedule_next_update()

    def refresh_ui(self) -> None:
        r = self.model.latest
        self.temp_var.set(f"Temp: {r.temperature_c:.2f} °C")
        self.hum_var.set(f"Humidity: {r.humidity_pct:.2f} %")
        self.pres_var.set(f"Pressure: {r.pressure_hpa:.2f} hPa")

        warnings = self.model.get_warning_state()

        self.temp_label.config(foreground="red" if warnings.temperature_high else "black")
        self.hum_label.config(foreground="red" if warnings.humidity_high else "black")
        self.pres_label.config(foreground="red" if warnings.pressure_high else "black")

    def refresh_chart(self) -> None:
        history = self.model.get_history()
        sensor_name = self.chart_sensor_var.get()
        y = history[sensor_name]

        self.ax.clear()
        self.ax.set_title(f"{sensor_name.capitalize()} Trend")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel(sensor_name.capitalize())

        if y:
            x = list(range(1, len(y) + 1))
            self.ax.plot(x, y, marker="o")
            self.ax.set_xlim(1, max(30, len(y)))
        else:
            self.ax.text(0.5, 0.5, "No data yet", ha="center", va="center", transform=self.ax.transAxes)

        self.canvas.draw()