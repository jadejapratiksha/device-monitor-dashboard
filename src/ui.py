# ui.py
# Tkinter UI layer (no simulation logic here)

import tkinter as tk
from tkinter import ttk

from model import DeviceModel


class DashboardUI:
    def __init__(self, root: tk.Tk, model: DeviceModel) -> None:
        self.root = root
        self.model = model

        self.root.title("Device Monitor Dashboard")
        self.root.geometry("700x400")

        # Update interval (ms) => 1000ms = 1 sec
        self.update_interval_ms = 1000

        # --- Top Frame: Status + Controls ---
        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        self.status_var = tk.StringVar(value="STOPPED")
        self.status_label = ttk.Label(top, textvariable=self.status_var)
        self.status_label.pack(side="left")

        self.start_stop_btn = ttk.Button(top, text="Start", command=self.toggle_start_stop)
        self.start_stop_btn.pack(side="left", padx=10)

        # Extra control: Reset history button
        self.reset_btn = ttk.Button(top, text="Reset", command=self.reset_history)
        self.reset_btn.pack(side="left")

        # --- Middle Frame: Sensor Readings ---
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

        # --- Bottom Frame: Threshold slider (extra control) ---
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

        # Timer handle so we can cancel if needed
        self._after_id = None

        # Initial UI refresh (but not running yet)
        self.refresh_ui()

    def on_threshold_change(self, _value: str) -> None:
        # Update model threshold when slider changes
        self.model.temp_threshold_c = float(self.threshold_var.get())
        self.threshold_value_label.config(text=f"{self.model.temp_threshold_c:.1f}")

    def toggle_start_stop(self) -> None:
        if self.model.running:
            self.model.stop()
            self.status_var.set("STOPPED")
            self.start_stop_btn.config(text="Start")
        else:
            self.model.start()
            self.status_var.set("RUNNING")
            self.start_stop_btn.config(text="Stop")
            self.schedule_next_update()

    def reset_history(self) -> None:
        self.model.reset_history()
        self.refresh_ui()

    def schedule_next_update(self) -> None:
        # Cancel any existing scheduled call
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)

        # Schedule the next update
        self._after_id = self.root.after(self.update_interval_ms, self.on_timer_tick)

    def on_timer_tick(self) -> None:
        if self.model.running:
            self.model.update_once()
            self.refresh_ui()
            self.schedule_next_update()

    def refresh_ui(self) -> None:
        # Update displayed text values
        r = self.model.latest
        self.temp_var.set(f"Temp: {r.temperature_c:.2f} °C")
        self.hum_var.set(f"Humidity: {r.humidity_pct:.2f} %")
        self.pres_var.set(f"Pressure: {r.pressure_hpa:.2f} hPa")

        # Warning visual (simple color change)
        warnings = self.model.get_warning_state()
        if warnings.temperature_high:
            self.temp_label.config(foreground="red")
        else:
            self.temp_label.config(foreground="black")