#!/usr/bin/env python3

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from services.config_service import ConfigService
from services.weather_service import (
    WeatherError,
    resolve_coordinates,
    test_open_meteo,
    test_openweather,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATION_FILE = PROJECT_DIR / "config" / "station.json"
SETTINGS_FILE = PROJECT_DIR / "config" / "settings.json"


class SettingsWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Settings")
        self.root.geometry("760x620")
        self.root.minsize(680, 540)

        self.station = ConfigService.load_json(STATION_FILE, {})
        self.settings = ConfigService.load_json(SETTINGS_FILE, {})
        weather = self.settings.get("weather", {})
        if not isinstance(weather, dict):
            weather = {}

        self.provider = tk.StringVar(value=weather.get("provider", "Open-Meteo"))
        self.use_grid = tk.BooleanVar(value=weather.get("use_station_grid", True))
        self.grid = tk.StringVar(value=self.station.get("grid_square", ""))
        self.latitude = tk.StringVar(value=str(weather.get("latitude", "")))
        self.longitude = tk.StringVar(value=str(weather.get("longitude", "")))
        self.api_key = tk.StringVar(value=weather.get("api_key", ""))
        self.refresh = tk.StringVar(value=str(weather.get("refresh_minutes", 20)))

        self.build_interface()
        self.update_states()

    def build_interface(self) -> None:
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="HamRadio-Pi Ultimate", font=("Arial", 22, "bold")).pack()
        ttk.Label(main, text="Settings", font=("Arial", 15)).pack(pady=(2, 14))

        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)
        general = ttk.Frame(notebook, padding=18)
        data = ttk.Frame(notebook, padding=18)
        notebook.add(general, text="General")
        notebook.add(data, text="Data Sources")

        ttk.Label(general, text="General settings will be added here.").pack(anchor="w")
        self.build_weather(data)

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(14, 0))
        ttk.Button(buttons, text="Cancel", command=self.root.destroy).pack(side="left")
        ttk.Button(buttons, text="Save Settings", command=self.save).pack(side="right")

    def build_weather(self, parent) -> None:
        frame = ttk.LabelFrame(parent, text="Weather", padding=16)
        frame.pack(fill="x")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Weather provider").grid(row=0, column=0, sticky="w", pady=7)
        combo = ttk.Combobox(frame, textvariable=self.provider, state="readonly", values=["Open-Meteo", "OpenWeather"])
        combo.grid(row=0, column=1, sticky="ew", pady=7)
        combo.bind("<<ComboboxSelected>>", lambda _e: self.update_states())

        ttk.Checkbutton(
            frame,
            text="Use the grid square from my station profile",
            variable=self.use_grid,
            command=self.update_states,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(7, 10))

        ttk.Label(frame, text="Station grid").grid(row=2, column=0, sticky="w", pady=7)
        self.grid_entry = ttk.Entry(frame, textvariable=self.grid)
        self.grid_entry.grid(row=2, column=1, sticky="ew", pady=7)

        ttk.Label(frame, text="Exact latitude").grid(row=3, column=0, sticky="w", pady=7)
        self.lat_entry = ttk.Entry(frame, textvariable=self.latitude)
        self.lat_entry.grid(row=3, column=1, sticky="ew", pady=7)

        ttk.Label(frame, text="Exact longitude").grid(row=4, column=0, sticky="w", pady=7)
        self.lon_entry = ttk.Entry(frame, textvariable=self.longitude)
        self.lon_entry.grid(row=4, column=1, sticky="ew", pady=7)

        ttk.Label(frame, text="API key").grid(row=5, column=0, sticky="w", pady=7)
        self.api_entry = ttk.Entry(frame, textvariable=self.api_key, show="•")
        self.api_entry.grid(row=5, column=1, sticky="ew", pady=7)

        ttk.Label(frame, text="Refresh every").grid(row=6, column=0, sticky="w", pady=7)
        ttk.Spinbox(frame, from_=5, to=120, textvariable=self.refresh, width=8).grid(row=6, column=1, sticky="w", pady=7)

        ttk.Button(frame, text="Test Weather Connection", command=self.test).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(14, 0)
        )

    def update_states(self) -> None:
        use_grid = self.use_grid.get()
        self.grid_entry.configure(state="normal" if use_grid else "disabled")
        self.lat_entry.configure(state="disabled" if use_grid else "normal")
        self.lon_entry.configure(state="disabled" if use_grid else "normal")
        self.api_entry.configure(state="normal" if self.provider.get() == "OpenWeather" else "disabled")

    def coordinates(self):
        return resolve_coordinates(
            self.use_grid.get(),
            self.grid.get(),
            self.latitude.get(),
            self.longitude.get(),
        )

    def test(self) -> None:
        try:
            coords = self.coordinates()
            result = (
                test_openweather(coords, self.api_key.get())
                if self.provider.get() == "OpenWeather"
                else test_open_meteo(coords)
            )
        except WeatherError as error:
            messagebox.showerror("Weather test failed", str(error))
            return
        messagebox.showinfo("Weather connection", result)

    def save(self) -> None:
        try:
            coords = self.coordinates()
            refresh = int(self.refresh.get())
        except (WeatherError, ValueError) as error:
            messagebox.showerror("Settings not saved", str(error))
            return

        settings = ConfigService.load_json(SETTINGS_FILE, {})
        settings["weather"] = {
            "provider": self.provider.get(),
            "use_station_grid": self.use_grid.get(),
            "grid_square": self.grid.get().strip().upper(),
            "latitude": coords.latitude,
            "longitude": coords.longitude,
            "api_key": self.api_key.get().strip(),
            "refresh_minutes": refresh,
        }
        ConfigService.save_json(SETTINGS_FILE, settings)
        messagebox.showinfo("Settings saved", "Weather settings have been saved.")
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    SettingsWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
