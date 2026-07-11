#!/usr/bin/env python3

from __future__ import annotations

import platform
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, ttk

from services.config_service import ConfigService
from services.weather_service import (
    WeatherError,
    fetch_current_weather,
    format_weather_summary,
)


PROJECT_DIR = Path(__file__).resolve().parent.parent
STATION_FILE = PROJECT_DIR / "config" / "station.json"
SETTINGS_FILE = PROJECT_DIR / "config" / "settings.json"
APPLICATION_FILE = PROJECT_DIR / "src" / "data" / "applications.json"
VERSION_FILE = PROJECT_DIR / "config" / "version.json"

WPSD_SCRIPT = PROJECT_DIR / "scripts" / "wpsd-card-builder.sh"
STATION_WIZARD = PROJECT_DIR / "src" / "station_wizard.py"
STATION_BUILDER = PROJECT_DIR / "src" / "station_builder.py"
APPLICATION_BROWSER = PROJECT_DIR / "src" / "application_browser.py"
HARDWARE = PROJECT_DIR / "src" / "hardware.py"
UPDATER = PROJECT_DIR / "src" / "updater.py"
SETTINGS = PROJECT_DIR / "src" / "settings.py"


class HamRadioPiUltimate:
    """Main HamRadio-Pi Ultimate dashboard."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate")
        self.root.geometry("1050x720")
        self.root.minsize(900, 620)

        self.station = ConfigService.load_json(
            STATION_FILE,
            {},
        )
        self.catalogue = ConfigService.load_json(
            APPLICATION_FILE,
            {"applications": []},
        )
        self.version_info = ConfigService.load_json(
            VERSION_FILE,
            {
                "version": "0.3.8",
                "edition": "Community",
            },
        )

        self.callsign_value = tk.StringVar()
        self.grid_value = tk.StringVar()
        self.local_time_value = tk.StringVar()
        self.utc_time_value = tk.StringVar()
        self.radio_value = tk.StringVar()
        self.sdr_value = tk.StringVar()
        self.station_type_value = tk.StringVar()
        self.weather_value = tk.StringVar(
            value="Loading..."
        )

        self.weather_refresh_job: str | None = None
        self.weather_loading = False

        self.build_interface()
        self.refresh_station_information()
        self.update_clocks()
        self.refresh_weather()

    def build_interface(self) -> None:
        main = ttk.Frame(
            self.root,
            padding=18,
        )
        main.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            main,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 26, "bold"),
        ).pack()

        ttk.Label(
            main,
            text="Build your station, not your software list.",
            font=("Arial", 11),
        ).pack(
            pady=(3, 15),
        )

        content = ttk.Frame(main)
        content.pack(
            fill="both",
            expand=True,
        )

        for column in (0, 1):
            content.columnconfigure(
                column,
                weight=1,
            )

        for row in (0, 1):
            content.rowconfigure(
                row,
                weight=1,
            )

        self.build_station_panel(content)
        self.build_status_panel(content)
        self.build_information_panel(content)
        self.build_tools_panel(content)

        version = self.version_info.get(
            "version",
            "Unknown",
        )
        edition = self.version_info.get(
            "edition",
            "Community",
        )

        ttk.Label(
            main,
            text=(
                f"HamRadio-Pi Ultimate {edition} Edition "
                f"— Version {version}"
            ),
            font=("Arial", 9),
        ).pack(
            pady=(12, 0),
        )

    @staticmethod
    def panel(
        parent,
        title,
        row,
        column,
    ):
        panel = ttk.LabelFrame(
            parent,
            text=title,
            padding=15,
        )
        panel.grid(
            row=row,
            column=column,
            padx=8,
            pady=8,
            sticky="nsew",
        )
        return panel

    def build_station_panel(
        self,
        parent,
    ) -> None:
        panel = self.panel(
            parent,
            "Station",
            0,
            0,
        )

        self.add_row(
            panel,
            0,
            "Callsign",
            self.callsign_value,
        )
        self.add_row(
            panel,
            1,
            "Grid",
            self.grid_value,
        )
        self.add_row(
            panel,
            2,
            "Station Type",
            self.station_type_value,
        )
        self.add_row(
            panel,
            3,
            "Current UTC",
            self.utc_time_value,
        )
        self.add_row(
            panel,
            4,
            "Local Time",
            self.local_time_value,
        )

        ttk.Button(
            panel,
            text="Edit Station Profile",
            command=self.open_station_wizard,
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(18, 0),
        )

        panel.columnconfigure(
            1,
            weight=1,
        )

    def build_status_panel(
        self,
        parent,
    ) -> None:
        panel = self.panel(
            parent,
            "Station Status",
            0,
            1,
        )

        ttk.Label(
            panel,
            text="Station Health",
            font=("Arial", 11, "bold"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=6,
        )

        ttk.Label(
            panel,
            text="Not checked",
        ).grid(
            row=0,
            column=1,
            sticky="e",
            pady=6,
        )

        self.add_row(
            panel,
            1,
            "Connected Radio",
            self.radio_value,
        )
        self.add_row(
            panel,
            2,
            "Connected SDR",
            self.sdr_value,
        )

        applications = self.catalogue.get(
            "applications",
            [],
        )
        count = (
            len(applications)
            if isinstance(
                applications,
                list,
            )
            else 0
        )

        ttk.Label(
            panel,
            text="Catalogue Applications",
            font=("Arial", 11, "bold"),
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=6,
        )

        ttk.Label(
            panel,
            text=str(count),
        ).grid(
            row=3,
            column=1,
            sticky="e",
            pady=6,
        )

        panel.columnconfigure(
            1,
            weight=1,
        )

    def build_information_panel(
        self,
        parent,
    ) -> None:
        panel = self.panel(
            parent,
            "Radio Information",
            1,
            0,
        )

        for row, item in enumerate(
            [
                "Latest DX Cluster Spots",
                "Solar Conditions",
                "Propagation",
            ]
        ):
            ttk.Label(
                panel,
                text=item,
                font=("Arial", 11, "bold"),
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=8,
            )

            ttk.Label(
                panel,
                text="Coming soon",
            ).grid(
                row=row,
                column=1,
                sticky="e",
                pady=8,
            )

        ttk.Label(
            panel,
            text="Weather",
            font=("Arial", 11, "bold"),
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=8,
        )

        ttk.Label(
            panel,
            textvariable=self.weather_value,
            wraplength=330,
            justify="right",
        ).grid(
            row=3,
            column=1,
            sticky="e",
            pady=8,
        )

        ttk.Button(
            panel,
            text="Refresh Weather",
            command=self.refresh_weather,
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 0),
        )

        panel.columnconfigure(
            1,
            weight=1,
        )

    def build_tools_panel(
        self,
        parent,
    ) -> None:
        panel = self.panel(
            parent,
            "Tools",
            1,
            1,
        )

        buttons = [
            (
                "Applications",
                self.open_application_browser,
            ),
            (
                "Build a Station",
                self.show_station_builder,
            ),
            (
                "WPSD SD Card Builder",
                self.open_wpsd_builder,
            ),
            (
                "Hardware",
                self.open_hardware,
            ),
            (
                "Updates",
                self.open_updater,
            ),
            (
                "Settings",
                self.open_settings,
            ),
        ]

        for index, (
            text,
            command,
        ) in enumerate(buttons):
            ttk.Button(
                panel,
                text=text,
                command=command,
            ).grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=6,
                pady=8,
            )

        panel.columnconfigure(
            0,
            weight=1,
        )
        panel.columnconfigure(
            1,
            weight=1,
        )

    @staticmethod
    def add_row(
        parent,
        row,
        title,
        value,
    ) -> None:
        ttk.Label(
            parent,
            text=title,
            font=("Arial", 11, "bold"),
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=6,
        )

        ttk.Label(
            parent,
            textvariable=value,
        ).grid(
            row=row,
            column=1,
            sticky="e",
            pady=6,
        )

    def refresh_station_information(self) -> None:
        self.station = ConfigService.load_json(
            STATION_FILE,
            {},
        )

        self.callsign_value.set(
            self.station.get("callsign")
            or "Not configured"
        )
        self.grid_value.set(
            self.station.get("grid_square")
            or "Not configured"
        )
        self.station_type_value.set(
            self.station.get("station_type")
            or "Not selected"
        )
        self.radio_value.set(
            self.station.get("preferred_radio")
            or "Not configured"
        )
        self.sdr_value.set(
            self.station.get("preferred_sdr")
            or "Not configured"
        )

    def update_clocks(self) -> None:
        self.utc_time_value.set(
            datetime.now(
                timezone.utc,
            ).strftime(
                "%H:%M:%S UTC",
            )
        )
        self.local_time_value.set(
            datetime.now()
            .astimezone()
            .strftime(
                "%H:%M:%S",
            )
        )
        self.root.after(
            1000,
            self.update_clocks,
        )

    def refresh_weather(self) -> None:
        if self.weather_loading:
            return

        if self.weather_refresh_job is not None:
            self.root.after_cancel(
                self.weather_refresh_job,
            )
            self.weather_refresh_job = None

        self.weather_loading = True
        self.weather_value.set(
            "Updating...",
        )

        threading.Thread(
            target=self._weather_worker,
            daemon=True,
        ).start()

    def _weather_worker(self) -> None:
        settings = ConfigService.load_json(
            SETTINGS_FILE,
            {},
        )
        station = ConfigService.load_json(
            STATION_FILE,
            {},
        )

        try:
            weather = fetch_current_weather(
                settings,
                station,
            )
            summary = format_weather_summary(
                weather,
            )
        except WeatherError as error:
            summary = str(error)

        self.root.after(
            0,
            lambda: self._finish_weather_refresh(
                summary,
                settings,
            ),
        )

    def _finish_weather_refresh(
        self,
        summary,
        settings,
    ) -> None:
        self.weather_value.set(
            summary,
        )
        self.weather_loading = False

        weather_settings = settings.get(
            "weather",
            {},
        )
        refresh_minutes = 20

        if isinstance(
            weather_settings,
            dict,
        ):
            try:
                refresh_minutes = int(
                    weather_settings.get(
                        "refresh_minutes",
                        20,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                refresh_minutes = 20

        refresh_minutes = max(
            5,
            min(
                refresh_minutes,
                120,
            ),
        )

        self.weather_refresh_job = self.root.after(
            refresh_minutes * 60 * 1000,
            self.refresh_weather,
        )

    def run_python_tool(
        self,
        path,
        title,
    ) -> None:
        if not path.exists():
            messagebox.showerror(
                title,
                f"{title} could not be found.",
            )
            return

        try:
            subprocess.run(
                [
                    sys.executable,
                    str(path),
                ],
                check=False,
            )
        except OSError as error:
            messagebox.showerror(
                title,
                f"{title} could not start:\n{error}",
            )

    def open_station_wizard(self) -> None:
        self.run_python_tool(
            STATION_WIZARD,
            "Station Setup Wizard",
        )
        self.refresh_station_information()
        self.refresh_weather()

    def show_station_builder(self) -> None:
        self.run_python_tool(
            STATION_BUILDER,
            "Station Builder",
        )
        self.refresh_station_information()

    def open_application_browser(self) -> None:
        self.run_python_tool(
            APPLICATION_BROWSER,
            "Applications",
        )

    def open_hardware(self) -> None:
        self.run_python_tool(
            HARDWARE,
            "Hardware Detection",
        )

    def open_updater(self) -> None:
        self.run_python_tool(
            UPDATER,
            "Update Manager",
        )

    def open_settings(self) -> None:
        self.run_python_tool(
            SETTINGS,
            "Settings",
        )
        self.refresh_station_information()
        self.refresh_weather()

    def open_wpsd_builder(self) -> None:
        if platform.system() != "Linux":
            messagebox.showinfo(
                "WPSD SD Card Builder",
                "The WPSD SD Card Builder runs on Raspberry Pi OS.",
            )
            return

        if not WPSD_SCRIPT.exists():
            messagebox.showerror(
                "WPSD SD Card Builder",
                "The WPSD builder script could not be found.",
            )
            return

        try:
            subprocess.Popen(
                [
                    "bash",
                    str(WPSD_SCRIPT),
                ]
            )
        except OSError as error:
            messagebox.showerror(
                "WPSD SD Card Builder",
                f"The WPSD builder could not start:\n{error}",
            )


def main() -> None:
    root = tk.Tk()
    HamRadioPiUltimate(root)
    root.mainloop()


if __name__ == "__main__":
    main()
