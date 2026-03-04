from model import DeviceModel

if __name__ == "__main__":
    m = DeviceModel(history_size=30)
    m.start()

    for _ in range(5):
        m.update_once()
        print("Latest:", m.latest)
        print("Warnings:", m.get_warning_state())
        print("Temp history length:", len(m.get_history()["temperature"]))