# simulator.py
# Generates simulated sensor readings (no hardware needed)

from dataclasses import dataclass
import math
import random
import time


@dataclass
class SensorReadings:
    temperature_c: float
    humidity_pct: float
    pressure_hpa: float


class SensorSimulator:
    # Clean OOP simulator: call next_readings() to get new values
    def __init__(self) -> None:
        self._t0 = time.time()
        self._step = 0

    def next_readings(self) -> SensorReadings:
        # Use elapsed time + step to create smooth-ish changing values
        elapsed = time.time() - self._t0
        self._step += 1

        # Temperature: ~22C baseline with sine variation and small random noise
        temp = 22.0 + 3.0 * math.sin(elapsed / 3.0) + random.uniform(-0.3, 0.3)

        # Humidity: ~45% baseline with slower sine variation + noise
        hum = 45.0 + 10.0 * math.sin(elapsed / 5.0 + 1.0) + random.uniform(-1.0, 1.0)

        # Pressure: ~1013 hPa baseline with gentle variation + noise
        pres = 1013.0 + 5.0 * math.sin(elapsed / 7.0 + 2.0) + random.uniform(-0.8, 0.8)

        return SensorReadings(
            temperature_c=round(temp, 2),
            humidity_pct=round(hum, 2),
            pressure_hpa=round(pres, 2),
        )