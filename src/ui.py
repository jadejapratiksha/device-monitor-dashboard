# ui.py
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from model import DeviceModel


class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=52, height=28, command=None):
        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent.cget("background") if "background" in parent.keys() else "white",
        )

        self.command = command
        self.state = False
        self.width_ = width
        self.height_ = height

        self.bg_off = "#cccccc"
        self.bg_on = "#14b8a6"
        self.knob_color = "white"

        self.bind("<Button-1>", self.toggle)
        self.draw()

    def set_bg(self, bg: str) -> None:
        self.configure(bg=bg)

    def draw(self) -> None:
        self.delete("all")

        bg_color = self.bg_on if self.state else self.bg_off
        pad = 2
        h = self.height_
        w = self.width_

        # Rounded track
        self.create_oval(pad, pad, h - pad, h - pad, fill=bg_color, outline=bg_color)
        self.create_oval(w - h + pad, pad, w - pad, h - pad, fill=bg_color, outline=bg_color)
        self.create_rectangle(h / 2, pad, w - h / 2, h - pad, fill=bg_color, outline=bg_color)

        # Knob
        knob_d = h - 6
        if self.state:
            x1 = w - knob_d - 3
        else:
            x1 = 3
        y1 = 3
        x2 = x1 + knob_d
        y2 = y1 + knob_d

        self.create_oval(x1, y1, x2, y2, fill=self.knob_color, outline=self.knob_color)

    def toggle(self, event=None) -> None:
        self.state = not self.state
        self.draw()

        if self.command:
            self.command(self.state)


class DashboardUI:
    def __init__(self, root: tk.Tk, model: DeviceModel) -> None:
        self.root = root
        self.model = model

        self.root.title("Device Monitor Dashboard")
        self.root.geometry("950x700")

        self.update_interval_ms = 1000
        self.dark_mode = False
        self._after_id = None

        # ---------------- Top Frame ----------------
        self.top = ttk.Frame(root, padding=10)
        self.top.pack(fill="x")

        self.status_var = tk.StringVar(value="STOPPED")
        self.status_label = ttk.Label(self.top, textvariable=self.status_var)
        self.status_label.pack(side="left")

        self.start_stop_btn = ttk.Button(self.top, text="Start", command=self.toggle_start_stop)
        self.start_stop_btn.pack(side="left", padx=10)

        self.reset_btn = ttk.Button(self.top, text="Reset", command=self.reset_history)
        self.reset_btn.pack(side="left", padx=5)

        self.export_btn = ttk.Button(self.top, text="Export CSV", command=self.export_csv)
        self.export_btn.pack(side="left", padx=5)

        ttk.Label(self.top, text="Dark Mode").pack(side="left", padx=(15, 6))
        self.theme_toggle = ToggleSwitch(self.top, command=self.toggle_theme)
        self.theme_toggle.pack(side="left", padx=(0, 12))

        ttk.Label(self.top, text="Chart sensor:").pack(side="left", padx=(10, 5))
        self.chart_sensor_var = tk.StringVar(value="temperature")
        self.chart_sensor_dropdown = ttk.Combobox(
            self.top,
            textvariable=self.chart_sensor_var,
            values=["temperature", "humidity", "pressure"],
            state="readonly",
            width=12,
        )
        self.chart_sensor_dropdown.pack(side="left")
        self.chart_sensor_dropdown.bind("<<ComboboxSelected>>", lambda event: self.refresh_chart())

        # ---------------- Middle Frame ----------------
        self.mid = ttk.Frame(root, padding=10)
        self.mid.pack(fill="x")

        self.temp_var = tk.StringVar(value="Temp: -- °C")
        self.hum_var = tk.StringVar(value="Humidity: -- %")
        self.pres_var = tk.StringVar(value="Pressure: -- hPa")

        self.temp_label = ttk.Label(self.mid, textvariable=self.temp_var, font=("Segoe UI", 12))
        self.hum_label = ttk.Label(self.mid, textvariable=self.hum_var, font=("Segoe UI", 12))
        self.pres_label = ttk.Label(self.mid, textvariable=self.pres_var, font=("Segoe UI", 12))

        self.temp_label.pack(anchor="w", pady=4)
        self.hum_label.pack(anchor="w", pady=4)
        self.pres_label.pack(anchor="w", pady=4)

        # ---------------- Threshold Frame ----------------
        self.bottom = ttk.Frame(root, padding=10)
        self.bottom.pack(fill="x")

        ttk.Label(self.bottom, text="Temp warning threshold (°C):").pack(side="left")

        self.threshold_var = tk.DoubleVar(value=self.model.temp_threshold_c)
        self.threshold_slider = ttk.Scale(
            self.bottom,
            from_=15.0,
            to=35.0,
            orient="horizontal",
            variable=self.threshold_var,
            command=self.on_threshold_change,
            length=250,
        )
        self.threshold_slider.pack(side="left", padx=10)

        self.threshold_value_label = ttk.Label(self.bottom, text=f"{self.model.temp_threshold_c:.1f}")
        self.threshold_value_label.pack(side="left")

        # ---------------- Chart Frame ----------------
        self.chart_frame = ttk.Frame(root, padding=10)
        self.chart_frame.pack(fill="both", expand=True)

        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        self.apply_theme()
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
        normal_fg = "white" if self.dark_mode else "black"

        self.temp_label.config(foreground="red" if warnings.temperature_high else normal_fg)
        self.hum_label.config(foreground="red" if warnings.humidity_high else normal_fg)
        self.pres_label.config(foreground="red" if warnings.pressure_high else normal_fg)

    def refresh_chart(self) -> None:
        history = self.model.get_history()
        sensor_name = self.chart_sensor_var.get()
        y = history[sensor_name]

        self.ax.clear()

        if self.dark_mode:
            fig_bg = "#222222"
            ax_bg = "#222222"
            text_color = "white"
            grid_color = "#555555"
        else:
            fig_bg = "white"
            ax_bg = "white"
            text_color = "black"
            grid_color = "#cccccc"

        self.figure.set_facecolor(fig_bg)
        self.ax.set_facecolor(ax_bg)

        self.ax.set_title(f"{sensor_name.capitalize()} Trend", color=text_color)
        self.ax.set_xlabel("Sample", color=text_color)
        self.ax.set_ylabel(sensor_name.capitalize(), color=text_color)
        self.ax.tick_params(axis="x", colors=text_color)
        self.ax.tick_params(axis="y", colors=text_color)
        self.ax.grid(True, color=grid_color, linestyle="--", alpha=0.6)

        for spine in self.ax.spines.values():
            spine.set_color(text_color)

        if y:
            x = list(range(1, len(y) + 1))
            self.ax.plot(x, y, marker="o")
            self.ax.set_xlim(1, max(30, len(y)))
        else:
            self.ax.text(
                0.5,
                0.5,
                "No data yet",
                ha="center",
                va="center",
                transform=self.ax.transAxes,
                color=text_color,
            )

        self.canvas.draw()

    def export_csv(self) -> None:
        rows = self.model.get_export_rows()

        if not rows:
            messagebox.showinfo("Export CSV", "No sensor data available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save sensor data as CSV",
        )

        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Sample", "Temperature (C)", "Humidity (%)", "Pressure (hPa)"])
            writer.writerows(rows)

        messagebox.showinfo("Export CSV", f"Sensor data exported successfully to:\n{file_path}")

    def toggle_theme(self, state: bool) -> None:
        self.dark_mode = state
        self.apply_theme()
        self.refresh_ui()
        self.refresh_chart()

    def apply_theme(self) -> None:
        if self.dark_mode:
            bg = "#222222"
            fg = "white"
        else:
            bg = "white"
            fg = "black"

        self.root.configure(bg=bg)
        self.theme_toggle.set_bg(bg)

        for widget in self.root.winfo_children():
            self._apply_bg_recursive(widget, bg, fg)

    def _apply_bg_recursive(self, widget, bg: str, fg: str) -> None:
        # Skip the custom switch background redraw here because it handles itself
        if isinstance(widget, ToggleSwitch):
            widget.set_bg(bg)
            return

        try:
            widget.configure(background=bg)
        except tk.TclError:
            pass

        try:
            widget.configure(foreground=fg)
        except tk.TclError:
            pass

        for child in widget.winfo_children():
            self._apply_bg_recursive(child, bg, fg)