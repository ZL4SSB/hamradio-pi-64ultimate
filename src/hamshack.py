#!/usr/bin/env python3

"""
HamRadio-Pi Ultimate
Main Dashboard
Version 0.3.0
"""

import json
import platform
import subprocess
import sys
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, ttk


PROJECT_DIR = Path(__file__).resolve().parent.parent
STATION_FILE = PROJECT_DIR / "config" / "station.json"
APPLICATION_FILE = PROJECT_DIR / "src" / "data" / "applications.json"
WPSD_SCRIPT = PROJECT_DIR / "scripts" / "wpsd-card-builder.sh"
STATION_WIZARD = PROJECT_DIR / "src" / "station_wizard.py"


class HamRadioPiUltimate:
    """Main HamRadio-Pi Ultimate dashboard."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        self.root.title("HamRadio-Pi Ultimate")
        self.root.geometry("1050x720")
        self.root.minsize(900, 620)

        self.station = self.load_json(STATION_FILE, {})
        self.catalogue = self.load_json(
            APPLICATION_FILE,
            {"applications": []},
        )

        self.callsign_value = tk.StringVar()
        self.grid_value = tk.StringVar()
        self.local_time_value = tk.StringVar()
        self.utc_time_value = tk.StringVar()
        self.radio_value = tk.StringVar()
        self.sdr_value = tk.StringVar()

        self.build_interface()
        self.refresh_station_information()
        self.update_clocks()

    @staticmethod
    def load_json(path: Path, default: dict) -> dict:
        """Load a JSON file, returning a default value on failure."""

        if not path.exists():
            return default

        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return default

    def build_interface(self) -> None:
        """Build the main dashboard."""

        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        self.build_header(main)

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)

        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self.build_station_panel(content)
        self.build_status_panel(content)
        self.build_information_panel(content)
        self.build_tools_panel(content)

        ttk.Label(
            main,
            text="HamRadio-Pi Ultimate Community Edition — Version 0.3.0",
            font=("Arial", 9),
        ).pack(pady=(12, 0))

    def build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 26, "bold"),
        ).pack()

        ttk.Label(
            header,
            text="Build your station, not your software list.",
            font=("Arial", 11),
        ).pack(pady=(3, 0))

    def build_station_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(
            parent,
            text="Station",
            padding=15,
        )
        panel.grid(
            row=0,
            column=0,
            padx=8,
            pady=8,
            sticky="nsew",
        )

        self.add_status_row(
            panel,
            0,
            "Callsign",
            self.callsign_value,
        )

        self.add_status_row(
            panel,
            1,
            "Grid",
            self.grid_value,
        )

        self.add_status_row(
            panel,
            2,
            "Current UTC",
            self.utc_time_value,
        )

        self.add_status_row(
            panel,
            3,
            "Local Time",
            self.local_time_value,
        )

        ttk.Button(
            panel,
            text="Edit Station Profile",
            command=self.open_station_wizard,
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(18, 0),
        )

        panel.columnconfigure(1, weight=1)

    def build_status_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(
            parent,
            text="Station Status",
            padding=15,
        )
        panel.grid(
            row=0,
            column=1,
            padx=8,
            pady=8,
            sticky="nsew",
        )

        ttk.Label(
            panel,
            text="Station Health",
            font=("Arial", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=6)

        ttk.Label(
            panel,
            text="Not checked",
        ).grid(row=0, column=1, sticky="e", pady=6)

        self.add_status_row(
            panel,
            1,
            "Connected Radio",
            self.radio_value,
        )

        self.add_status_row(
            panel,
            2,
            "Connected SDR",
            self.sdr_value,
        )

        application_count = len(
            self.catalogue.get("applications", [])
        )

        ttk.Label(
            panel,
            text="Catalogue Applications",
            font=("Arial", 11, "bold"),
        ).grid(row=3, column=0, sticky="w", pady=6)

        ttk.Label(
            panel,
            text=str(application_count),
        ).grid(row=3, column=1, sticky="e", pady=6)

        panel.columnconfigure(1, weight=1)

    def build_information_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(
            parent,
            text="Radio Information",
            padding=15,
        )
        panel.grid(
            row=1,
            column=0,
            padx=8,
            pady=8,
            sticky="nsew",
        )

        items = [
            "Latest DX Cluster Spots",
            "Solar Conditions",
            "Propagation",
            "Weather",
        ]

        for row, item in enumerate(items):
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

        panel.columnconfigure(1, weight=1)

    def build_tools_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(
            parent,
            text="Tools",
            padding=15,
        )
        panel.grid(
            row=1,
            column=1,
            padx=8,
            pady=8,
            sticky="nsew",
        )

        buttons = [
            ("Applications", self.show_applications),
            ("Build a Station", self.show_station_builder),
            ("WPSD SD Card Builder", self.open_wpsd_builder),
            ("Hardware", self.show_hardware),
            ("Updates", self.show_updates),
            ("Settings", self.open_station_wizard),
        ]

        for index, (text, command) in enumerate(buttons):
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

        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)

    @staticmethod
    def add_status_row(
        parent: ttk.LabelFrame,
        row: int,
        title: str,
        value: tk.StringVar,
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
        """Reload and display station information."""

        self.station = self.load_json(STATION_FILE, {})

        self.callsign_value.set(
            self.station.get("callsign", "Not configured")
        )

        self.grid_value.set(
            self.station.get("grid_square", "Not configured")
        )

        self.radio_value.set(
            self.station.get(
                "preferred_radio",
                "Not configured",
            )
            or "Not configured"
        )

        self.sdr_value.set(
            self.station.get(
                "preferred_sdr",
                "Not configured",
            )
            or "Not configured"
        )

    def update_clocks(self) -> None:
        """Update UTC and local clocks every second."""

        utc_now = datetime.now(timezone.utc)
        local_now = datetime.now().astimezone()

        self.utc_time_value.set(
            utc_now.strftime("%H:%M:%S UTC")
        )

        self.local_time_value.set(
            local_now.strftime("%H:%M:%S")
        )

        self.root.after(1000, self.update_clocks)

    def open_station_wizard(self) -> None:
        """Open the station setup wizard."""

        try:
            subprocess.run(
                [sys.executable, str(STATION_WIZARD)],
                check=False,
            )
        except OSError as error:
            messagebox.showerror(
                "Station Setup",
                f"The Station Setup Wizard could not start:\n{error}",
            )
            return

        self.refresh_station_information()

    def open_wpsd_builder(self) -> None:
        """Open the Linux WPSD SD Card Builder."""

        if platform.system() != "Linux":
            messagebox.showinfo(
                "WPSD SD Card Builder",
                "The WPSD SD Card Builder runs on Raspberry Pi OS.\n\n"
                "Push these changes to GitHub and test it on the Pi.",
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
                ["bash", str(WPSD_SCRIPT)],
            )
        except OSError as error:
            messagebox.showerror(
                "WPSD SD Card Builder",
                f"The WPSD builder could not start:\n{error}",
            )

    def show_applications(self) -> None:
        applications = self.catalogue.get("applications", [])

        names = "\n".join(
            f"• {application.get('name', 'Unknown')}"
            for application in applications
        )

        messagebox.showinfo(
            "Applications",
            names or "No applications are currently listed.",
        )

    @staticmethod
    def show_station_builder() -> None:
        messagebox.showinfo(
            "Build a Station",
            "The Station Builder will be added next.",
        )

    @staticmethod
    def show_hardware() -> None:
        messagebox.showinfo(
            "Hardware",
            "Automatic hardware detection will be added soon.",
        )

    @staticmethod
    def show_updates() -> None:
        messagebox.showinfo(
            "Updates",
            "The update manager will be added soon.",
        )


def main() -> None:
    root = tk.Tk()
    HamRadioPiUltimate(root)
    root.mainloop()


if __name__ == "__main__":
    main()