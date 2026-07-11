#!/usr/bin/env python3

"""
HamRadio-Pi Ultimate
Station Setup Wizard
Version 0.1.0
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_DIR / "config"
STATION_FILE = CONFIG_DIR / "station.json"


class StationWizard:
    """Collects and saves the operator's station information."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        self.root.title("HamRadio-Pi Ultimate - Station Setup")
        self.root.geometry("650x620")
        self.root.minsize(600, 560)

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        self.callsign = tk.StringVar()
        self.operator_name = tk.StringVar()
        self.grid_square = tk.StringVar()
        self.country = tk.StringVar(value="New Zealand")
        self.dmr_id = tk.StringVar()
        self.preferred_radio = tk.StringVar()
        self.preferred_sdr = tk.StringVar()
        self.station_type = tk.StringVar(
            value="Recommended Ham Station"
        )

        self.load_existing_settings()
        self.build_interface()

    def build_interface(self) -> None:
        """Create the setup wizard interface."""

        main = ttk.Frame(self.root, padding=24)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 22, "bold"),
        ).pack(pady=(0, 5))

        ttk.Label(
            main,
            text="Station Setup Wizard",
            font=("Arial", 15),
        ).pack(pady=(0, 20))

        form = ttk.Frame(main)
        form.pack(fill="both", expand=True)

        self.add_entry(form, 0, "Callsign", self.callsign)
        self.add_entry(form, 1, "Operator name", self.operator_name)
        self.add_entry(form, 2, "Grid square", self.grid_square)
        self.add_entry(form, 3, "Country", self.country)
        self.add_entry(form, 4, "DMR ID", self.dmr_id)

        ttk.Label(
            form,
            text="Preferred radio",
        ).grid(row=5, column=0, sticky="w", padx=5, pady=8)

        radio_box = ttk.Combobox(
            form,
            textvariable=self.preferred_radio,
            values=[
                "",
                "Xiegu G90",
                "Yaesu",
                "Icom",
                "Kenwood",
                "FlexRadio",
                "Other",
            ],
        )
        radio_box.grid(
            row=5,
            column=1,
            sticky="ew",
            padx=5,
            pady=8,
        )

        ttk.Label(
            form,
            text="Preferred SDR",
        ).grid(row=6, column=0, sticky="w", padx=5, pady=8)

        sdr_box = ttk.Combobox(
            form,
            textvariable=self.preferred_sdr,
            values=[
                "",
                "RTL-SDR",
                "Airspy",
                "HackRF",
                "SDRplay",
                "LimeSDR",
                "PlutoSDR",
                "Other",
            ],
        )
        sdr_box.grid(
            row=6,
            column=1,
            sticky="ew",
            padx=5,
            pady=8,
        )

        ttk.Label(
            form,
            text="Station type",
        ).grid(row=7, column=0, sticky="w", padx=5, pady=8)

        station_box = ttk.Combobox(
            form,
            textvariable=self.station_type,
            state="readonly",
            values=[
                "Recommended Ham Station",
                "Digital Modes Station",
                "SDR Receiver Station",
                "APRS and Packet Station",
                "Satellite Station",
                "Contest Station",
                "Emergency Communications Station",
                "MMDVM Hotspot",
                "Headless Radio Server",
            ],
        )
        station_box.grid(
            row=7,
            column=1,
            sticky="ew",
            padx=5,
            pady=8,
        )

        form.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(main)
        button_frame.pack(fill="x", pady=(20, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.root.destroy,
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Save Station",
            command=self.save_station,
        ).pack(side="right")

        ttk.Label(
            main,
            text="Your station information is stored locally.",
            font=("Arial", 9),
        ).pack(pady=(15, 0))

    @staticmethod
    def add_entry(
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
    ) -> None:
        """Add a labelled text entry to the form."""

        ttk.Label(
            parent,
            text=label,
        ).grid(row=row, column=0, sticky="w", padx=5, pady=8)

        ttk.Entry(
            parent,
            textvariable=variable,
        ).grid(row=row, column=1, sticky="ew", padx=5, pady=8)

    def load_existing_settings(self) -> None:
        """Load existing station settings if available."""

        if not STATION_FILE.exists():
            return

        try:
            with STATION_FILE.open("r", encoding="utf-8") as file:
                settings = json.load(file)
        except (OSError, json.JSONDecodeError):
            return

        self.callsign.set(settings.get("callsign", ""))
        self.operator_name.set(settings.get("operator_name", ""))
        self.grid_square.set(settings.get("grid_square", ""))
        self.country.set(settings.get("country", "New Zealand"))
        self.dmr_id.set(settings.get("dmr_id", ""))
        self.preferred_radio.set(
            settings.get("preferred_radio", "")
        )
        self.preferred_sdr.set(
            settings.get("preferred_sdr", "")
        )
        self.station_type.set(
            settings.get(
                "station_type",
                "Recommended Ham Station",
            )
        )

    def save_station(self) -> None:
        """Validate and save station information."""

        callsign = self.callsign.get().strip().upper()
        grid_square = self.grid_square.get().strip().upper()
        dmr_id = self.dmr_id.get().strip()

        if not callsign:
            messagebox.showwarning(
                "Missing callsign",
                "Please enter your amateur radio callsign.",
            )
            return

        if dmr_id and not dmr_id.isdigit():
            messagebox.showwarning(
                "Invalid DMR ID",
                "The DMR ID must contain numbers only.",
            )
            return

        station_data = {
            "callsign": callsign,
            "operator_name": self.operator_name.get().strip(),
            "grid_square": grid_square,
            "country": self.country.get().strip(),
            "dmr_id": dmr_id,
            "preferred_radio": self.preferred_radio.get().strip(),
            "preferred_sdr": self.preferred_sdr.get().strip(),
            "station_type": self.station_type.get().strip(),
            "edition": "Community",
        }

        try:
            with STATION_FILE.open("w", encoding="utf-8") as file:
                json.dump(
                    station_data,
                    file,
                    indent=4,
                )
        except OSError as error:
            messagebox.showerror(
                "Save failed",
                f"The station profile could not be saved:\n{error}",
            )
            return

        messagebox.showinfo(
            "Station saved",
            f"Station profile saved for {callsign}.",
        )

        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    StationWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()