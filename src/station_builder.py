#!/usr/bin/env python3

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATION_FILE = PROJECT_DIR / "config" / "station.json"

STATION_PROFILES = {
    "Recommended Ham Station": {
        "description": "A balanced selection for most amateur radio operators.",
        "groups": ["Digital Modes", "SDR", "APRS and Packet", "Satellite", "Logging", "Radio Programming"],
        "estimated_gb": 15,
    },
    "Digital Modes Station": {
        "description": "Software for FT8, FT4, JS8, RTTY, PSK and related modes.",
        "groups": ["WSJT-X", "JS8Call", "FLDIGI", "FLRIG", "Hamlib", "Logging"],
        "estimated_gb": 6,
    },
    "SDR Receiver Station": {
        "description": "SDR receivers, signal analysis and RTL-SDR support.",
        "groups": ["GQRX", "RTL-SDR Tools", "GNU Radio", "SoapySDR"],
        "estimated_gb": 10,
    },
    "APRS and Packet Station": {
        "description": "APRS, packet radio, GPS, AX.25 and software TNC tools.",
        "groups": ["Direwolf", "Xastir", "AX.25 Tools", "GPS Tools"],
        "estimated_gb": 4,
    },
    "Satellite Station": {
        "description": "Satellite tracking, Doppler control and radio control.",
        "groups": ["Gpredict", "Hamlib", "Satellite Decoders", "SDR Support"],
        "estimated_gb": 5,
    },
    "MMDVM Hotspot": {
        "description": "Prepare WPSD for a separate Raspberry Pi and MMDVM board.",
        "groups": ["WPSD SD Card Builder", "MMDVM Documentation", "Digital Voice Tools"],
        "estimated_gb": 2,
    },
}

class StationBuilder:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Station Builder")
        self.root.geometry("820x620")
        self.root.minsize(720, 540)

        self.selected = tk.StringVar(value="Recommended Ham Station")
        self.description = tk.StringVar()
        self.storage = tk.StringVar()

        self.load_existing()
        self.build_interface()
        self.update_details()

    def build_interface(self) -> None:
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="HamRadio-Pi Ultimate", font=("Arial", 22, "bold")).pack()
        ttk.Label(main, text="Station Builder", font=("Arial", 15)).pack(pady=(2, 18))

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)

        left = ttk.LabelFrame(content, text="Choose a station", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = ttk.LabelFrame(content, text="Station details", padding=16)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        for name in STATION_PROFILES:
            ttk.Radiobutton(
                left, text=name, value=name, variable=self.selected,
                command=self.update_details
            ).pack(anchor="w", fill="x", pady=5)

        ttk.Label(right, textvariable=self.description, wraplength=430, justify="left").pack(anchor="w")
        self.listbox = tk.Listbox(right, height=12)
        self.listbox.pack(fill="both", expand=True, pady=12)
        ttk.Label(right, textvariable=self.storage, font=("Arial", 11, "bold")).pack(anchor="w")

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(18, 0))
        ttk.Button(buttons, text="Cancel", command=self.root.destroy).pack(side="left")
        ttk.Button(buttons, text="Save Station Choice", command=self.save_choice).pack(side="right")

    def load_existing(self) -> None:
        if not STATION_FILE.exists():
            return
        try:
            data = json.loads(STATION_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        name = data.get("station_type")
        if name in STATION_PROFILES:
            self.selected.set(name)

    def update_details(self) -> None:
        profile = STATION_PROFILES[self.selected.get()]
        self.description.set(profile["description"])
        self.storage.set(f"Estimated storage required: {profile['estimated_gb']} GB")
        self.listbox.delete(0, tk.END)
        for group in profile["groups"]:
            self.listbox.insert(tk.END, f"• {group}")

    def save_choice(self) -> None:
        data = {}
        if STATION_FILE.exists():
            try:
                data = json.loads(STATION_FILE.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = {}

        name = self.selected.get()
        profile = STATION_PROFILES[name]
        data["station_type"] = name
        data["station_groups"] = profile["groups"]
        data["estimated_storage_gb"] = profile["estimated_gb"]

        STATION_FILE.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
        messagebox.showinfo("Station saved", f"{name} has been selected.")
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    StationBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
