import os
import sys
import unittest

# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from model import DeviceModel
from simulator import SensorSimulator, SensorReadings


class TestDeviceModel(unittest.TestCase):
    def setUp(self):
        self.model = DeviceModel(history_size=3)

    def test_initial_state(self):
        self.assertFalse(self.model.running)
        self.assertEqual(self.model.latest.temperature_c, 0.0)
        self.assertEqual(self.model.latest.humidity_pct, 0.0)
        self.assertEqual(self.model.latest.pressure_hpa, 0.0)

        history = self.model.get_history()
        self.assertEqual(history["temperature"], [])
        self.assertEqual(history["humidity"], [])
        self.assertEqual(history["pressure"], [])

    def test_start_and_stop(self):
        self.model.start()
        self.assertTrue(self.model.running)

        self.model.stop()
        self.assertFalse(self.model.running)

    def test_update_once_adds_history(self):
        self.model.update_once()

        history = self.model.get_history()
        self.assertEqual(len(history["temperature"]), 1)
        self.assertEqual(len(history["humidity"]), 1)
        self.assertEqual(len(history["pressure"]), 1)

    def test_history_limit(self):
        for _ in range(5):
            self.model.update_once()

        history = self.model.get_history()
        self.assertEqual(len(history["temperature"]), 3)
        self.assertEqual(len(history["humidity"]), 3)
        self.assertEqual(len(history["pressure"]), 3)

    def test_reset_history(self):
        for _ in range(3):
            self.model.update_once()

        self.model.reset_history()
        history = self.model.get_history()

        self.assertEqual(history["temperature"], [])
        self.assertEqual(history["humidity"], [])
        self.assertEqual(history["pressure"], [])

        self.assertEqual(self.model.latest.temperature_c, 0.0)
        self.assertEqual(self.model.latest.humidity_pct, 0.0)
        self.assertEqual(self.model.latest.pressure_hpa, 0.0)

    def test_warning_state(self):
        # Force values manually for predictable testing
        self.model.latest = SensorReadings(30.0, 70.0, 1030.0)

        warnings = self.model.get_warning_state()

        self.assertTrue(warnings.temperature_high)
        self.assertTrue(warnings.humidity_high)
        self.assertTrue(warnings.pressure_high)

    def test_export_rows(self):
        for _ in range(3):
            self.model.update_once()

        rows = self.model.get_export_rows()

        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[0]), 4)  # sample, temp, hum, pressure
        self.assertEqual(rows[0][0], 1)


class TestSensorSimulator(unittest.TestCase):
    def test_next_readings_returns_sensor_readings(self):
        sim = SensorSimulator()
        result = sim.next_readings()

        self.assertIsInstance(result, SensorReadings)

    def test_next_readings_fields_are_numbers(self):
        sim = SensorSimulator()
        result = sim.next_readings()

        self.assertIsInstance(result.temperature_c, float)
        self.assertIsInstance(result.humidity_pct, float)
        self.assertIsInstance(result.pressure_hpa, float)


if __name__ == "__main__":
    unittest.main()