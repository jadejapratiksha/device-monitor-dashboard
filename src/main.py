# main.py
import tkinter as tk

from model import DeviceModel
from ui import DashboardUI


def main() -> None:
    root = tk.Tk()
    model = DeviceModel(history_size=30)
    DashboardUI(root, model)
    root.mainloop()


if __name__ == "__main__":
    main()