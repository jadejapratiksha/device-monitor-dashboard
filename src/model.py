# model.py
# Holds current sensor values + last N history points + threshold logic

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List

from simulator import SensorReadings, SensorSimulator


@dataclass
class WarningState:
    # Represents whether any sensor is in warning state
    temperature_high: bool
    humidity_high: bool
    pressure_high: bool


class DeviceModel:
    # Pure logic/data model: no GUI code here
    def __init__(self, history_size: int = 30) -> None:
        self._sim = SensorSimulator()

        self.running: bool = False

        # Thresholds (can be adjusted by UI later)
        self.temp_threshold_c: float = 25.0
        self.hum_threshold_pct: float = 60.0
        self.pres_threshold_hpa: float = 1020.0

        # Latest readings
        self.latest: SensorReadings = SensorReadings(0.0, 0.0, 0.0)

        # History buffers (keep last history_size points)
        self._hist_temp: Deque[float] = deque(maxlen=history_size)
        self._hist_hum: Deque[float] = deque(maxlen=history_size)
        self._hist_pres: Deque[float] = deque(maxlen=history_size)

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def reset_history(self) -> None:
        self._hist_temp.clear()
        self._hist_hum.clear()
        self._hist_pres.clear()
        # Reset latest values too (so UI shows zeros/placeholder)
        self.latest = SensorReadings(0.0, 0.0, 0.0)

    def update_once(self) -> None:
        # Generate new readings and push into history
        self.latest = self._sim.next_readings()
        self._hist_temp.append(self.latest.temperature_c)
        self._hist_hum.append(self.latest.humidity_pct)
        self._hist_pres.append(self.latest.pressure_hpa)

    def get_history(self) -> Dict[str, List[float]]:
        # UI will call this for charting
        return {
            "temperature": list(self._hist_temp),
            "humidity": list(self._hist_hum),
            "pressure": list(self._hist_pres),
        }

    def get_warning_state(self) -> WarningState:
        # Decide if each sensor exceeds threshold
        return WarningState(
            temperature_high=self.latest.temperature_c > self.temp_threshold_c,
            humidity_high=self.latest.humidity_pct > self.hum_threshold_pct,
            pressure_high=self.latest.pressure_hpa > self.pres_threshold_hpa,
        )