#!/usr/bin/env python3

"""Settings window for HamRadio-Pi Ultimate."""

from __future__ import annotations

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
    """HamRadio-Pi Ultimate settings window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Settings")
        self.root.geometry("760x620")
        self.root.minsize(680, 540)

        self.station = ConfigService.load_json(
            STATION_FILE,
            {},
        )
        self.settings = ConfigService.load_json(
            SETTINGS_FILE,
            {},
        )

        weather = self.settings.get("weather", {})
        if not isinstance(weather, dict):
            weather = {}

        self.weather_provider = tk.StringVar(
            value=weather.get("provider", "Open-Meteo")
        )
        self.use_station_grid = tk.BooleanVar(
            value=weather.get("use_station_grid", True)
        )
        self.grid_square = tk.StringVar(
            value=self.station.get("grid_square", "")
        )
        self.latitude = tk.StringVar(
            value=str(weather.get("latitude", ""))
        )
        self.longitude = tk.StringVar(
            value=str(weather.get("longitude", ""))
        )
        self.api_key = tk.StringVar(
            value=weather.get("api_key", "")
        )
        self.refresh_minutes = tk.StringVar(
            value=str(weather.get("refresh_minutes", 20))
        )

        self.build_interface()
        self.update_field_states()

    def build_interface(self) -> None:
        """Create all settings pages."""

        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 22, "bold"),
        ).pack()

        ttk.Label(
            main,
            text="Settings",
            font=("Arial", 15),
        ).pack(pady=(2, 14))

        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)

        general_tab = ttk.Frame(notebook, padding=18)
        data_tab = ttk.Frame(notebook, padding=18)

        notebook.add(general_tab, text="General")
        notebook.add(data_tab, text="Data Sources")

        ttk.Label(
            general_tab,
            text="General settings will be added here.",
        ).pack(anchor="w")

        self.build_data_sources_tab(data_tab)

        button_frame = ttk.Frame(main)
        button_frame.pack(fill="x", pady=(14, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.root.destroy,
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
        ).pack(side="right")

    def build_data_sources_tab(self, parent: ttk.Frame) -> None:
        """Create weather data-source settings."""

        weather_frame = ttk.LabelFrame(
            parent,
            text="Weather",
            padding=16,
        )
        weather_frame.pack(fill="x")

        ttk.Label(
            weather_frame,
            text="Weather provider",
        ).grid(row=0, column=0, sticky="w", pady=7)

        provider_box = ttk.Combobox(
            weather_frame,
            textvariable=self.weather_provider,
            state="readonly",
            values=[
                "Open-Meteo",
                "OpenWeather",
            ],
        )
        provider_box.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=7,
        )
        provider_box.bind(
            "<<ComboboxSelected>>",
            lambda _event: self.update_field_states(),
        )

        ttk.Checkbutton(
            weather_frame,
            text="Use the grid square from my station profile",
            variable=self.use_station_grid,
            command=self.update_field_states,
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(7, 10),
        )

        ttk.Label(
            weather_frame,
            text="Station grid",
        ).grid(row=2, column=0, sticky="w", pady=7)

        self.grid_entry = ttk.Entry(
            weather_frame,
            textvariable=self.grid_square,
        )
        self.grid_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            pady=7,
        )

        ttk.Label(
            weather_frame,
            text="Exact latitude",
        ).grid(row=3, column=0, sticky="w", pady=7)

        self.latitude_entry = ttk.Entry(
            weather_frame,
            textvariable=self.latitude,
        )
        self.latitude_entry.grid(
            row=3,
            column=1,
            sticky="ew",
            pady=7,
        )

        ttk.Label(
            weather_frame,
            text="Exact longitude",
        ).grid(row=4, column=0, sticky="w", pady=7)

        self.longitude_entry = ttk.Entry(
            weather_frame,
            textvariable=self.longitude,
        )
        self.longitude_entry.grid(
            row=4,
            column=1,
            sticky="ew",
            pady=7,
        )

        ttk.Label(
            weather_frame,
            text="API key",
        ).grid(row=5, column=0, sticky="w", pady=7)

        self.api_entry = ttk.Entry(
            weather_frame,
            textvariable=self.api_key,
            show="•",
        )
        self.api_entry.grid(
            row=5,
            column=1,
            sticky="ew",
            pady=7,
        )

        ttk.Label(
            weather_frame,
            text="Refresh every",
        ).grid(row=6, column=0, sticky="w", pady=7)

        refresh_frame = ttk.Frame(weather_frame)
        refresh_frame.grid(
            row=6,
            column=1,
            sticky="w",
            pady=7,
        )

        ttk.Spinbox(
            refresh_frame,
            from_=5,
            to=120,
            textvariable=self.refresh_minutes,
            width=8,
        ).pack(side="left")

        ttk.Label(
            refresh_frame,
            text="minutes",
        ).pack(side="left", padx=(6, 0))

        ttk.Button(
            weather_frame,
            text="Test Weather Connection",
            command=self.test_connection,
        ).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(14, 0),
        )

        ttk.Label(
            weather_frame,
            text=(
                "Open-Meteo requires no API key. OpenWeather "
                "requires an API key from your OpenWeather account."
            ),
            wraplength=620,
            justify="left",
        ).grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(12, 0),
        )

        weather_frame.columnconfigure(1, weight=1)

    def update_field_states(self) -> None:
        """Enable only the fields needed by the selected settings."""

        use_grid = self.use_station_grid.get()
        provider = self.weather_provider.get()

        self.grid_entry.configure(
            state="normal" if use_grid else "disabled"
        )
        self.latitude_entry.configure(
            state="disabled" if use_grid else "normal"
        )
        self.longitude_entry.configure(
            state="disabled" if use_grid else "normal"
        )
        self.api_entry.configure(
            state="normal"
            if provider == "OpenWeather"
            else "disabled"
        )

    def selected_coordinates(self):
        """Resolve the location chosen in Settings."""

        return resolve_coordinates(
            use_station_grid=self.use_station_grid.get(),
            station_grid=self.grid_square.get(),
            exact_latitude=self.latitude.get(),
            exact_longitude=self.longitude.get(),
        )

    def test_connection(self) -> None:
        """Test the selected weather provider."""

        try:
            coordinates = self.selected_coordinates()

            if self.weather_provider.get() == "OpenWeather":
                message = test_openweather(
                    coordinates,
                    self.api_key.get(),
                )
            else:
                message = test_open_meteo(coordinates)
        except WeatherError as error:
            messagebox.showerror(
                "Weather test failed",
                str(error),
            )
            return

        messagebox.showinfo(
            "Weather connection",
            message,
        )

    def save_settings(self) -> None:
        """Validate and save settings."""

        try:
            coordinates = self.selected_coordinates()
            refresh = int(self.refresh_minutes.get())
        except (WeatherError, ValueError) as error:
            messagebox.showerror(
                "Settings not saved",
                str(error),
            )
            return

        if not 5 <= refresh <= 120:
            messagebox.showerror(
                "Settings not saved",
                "Weather refresh time must be between 5 and 120 minutes.",
            )
            return

        settings = ConfigService.load_json(
            SETTINGS_FILE,
            {},
        )

        settings["weather"] = {
            "provider": self.weather_provider.get(),
            "use_station_grid": self.use_station_grid.get(),
            "grid_square": self.grid_square.get().strip().upper(),
            "latitude": coordinates.latitude,
            "longitude": coordinates.longitude,
            "api_key": self.api_key.get().strip(),
            "refresh_minutes": refresh,
        }

        try:
            ConfigService.save_json(
                SETTINGS_FILE,
                settings,
            )
        except OSError as error:
            messagebox.showerror(
                "Settings not saved",
                f"Settings could not be saved:\n{error}",
            )
            return

        messagebox.showinfo(
            "Settings saved",
            "Weather data-source settings have been saved.",
        )
        self.root.destroy()


def main() -> None:
    """Open the Settings window."""

    root = tk.Tk()
    SettingsWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
