#!/usr/bin/env python3

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_DIR / "config"
STATION_FILE = CONFIG_DIR / "station.json"

STATION_PROFILES = {
    "Recommended Ham Station": {
        "description": "A balanced selection for most amateur radio operators.",
        "groups": [
            "Digital Modes",
            "SDR",
            "APRS and Packet",
            "Satellite",
            "Logging",
            "Radio Programming",
        ],
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
    "Contest Station": {
        "description": "Logging, rig control and contest operating tools.",
        "groups": ["Contest Logging", "Hamlib", "Digital Modes", "CW Tools"],
        "estimated_gb": 8,
    },
    "Emergency Communications Station": {
        "description": "Packet, APRS, GPS and logging for field communications.",
        "groups": ["Direwolf", "APRS", "Packet", "GPS", "Logging"],
        "estimated_gb": 9,
    },
    "MMDVM Hotspot": {
        "description": "Prepare WPSD for a separate Raspberry Pi and MMDVM board.",
        "groups": [
            "WPSD SD Card Builder",
            "MMDVM Documentation",
            "Digital Voice Tools",
        ],
        "estimated_gb": 2,
    },
    "Headless Radio Server": {
        "description": "Remote SDR, APRS and streaming without a local desktop.",
        "groups": ["Remote SDR", "APRS Services", "Streaming"],
        "estimated_gb": 10,
    },
}


class StationBuilder:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Station Builder")
        self.root.geometry("820x620")
        self.root.minsize(720, 540)

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        self.selected_profile = tk.StringVar(
            value="Recommended Ham Station"
        )
        self.description_value = tk.StringVar()
        self.storage_value = tk.StringVar()

        self.load_existing_choice()
        self.build_interface()
        self.update_profile_details()

    def build_interface(self) -> None:
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 22, "bold"),
        ).pack()
        ttk.Label(
            main,
            text="Station Builder",
            font=("Arial", 15),
        ).pack(pady=(2, 18))

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        profile_frame = ttk.LabelFrame(
            content,
            text="Choose a station",
            padding=12,
        )
        profile_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        details_frame = ttk.LabelFrame(
            content,
            text="Station details",
            padding=16,
        )
        details_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )

        for profile_name in STATION_PROFILES:
            ttk.Radiobutton(
                profile_frame,
                text=profile_name,
                value=profile_name,
                variable=self.selected_profile,
                command=self.update_profile_details,
            ).pack(anchor="w", fill="x", pady=5)

        ttk.Label(
            details_frame,
            textvariable=self.description_value,
            wraplength=430,
            justify="left",
            font=("Arial", 11),
        ).pack(anchor="w", fill="x", pady=(0, 16))

        ttk.Label(
            details_frame,
            text="Included software groups",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")

        self.group_list = tk.Listbox(
            details_frame,
            height=12,
            activestyle="none",
        )
        self.group_list.pack(
            fill="both",
            expand=True,
            pady=(8, 14),
        )

        ttk.Label(
            details_frame,
            textvariable=self.storage_value,
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")

        button_frame = ttk.Frame(main)
        button_frame.pack(fill="x", pady=(18, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.root.destroy,
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Save Station Choice",
            command=self.save_station_choice,
        ).pack(side="right")

    def load_existing_choice(self) -> None:
        if not STATION_FILE.exists():
            return
        try:
            with STATION_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return

        existing = data.get("station_type")
        if existing in STATION_PROFILES:
            self.selected_profile.set(existing)

    def update_profile_details(self) -> None:
        profile = STATION_PROFILES[self.selected_profile.get()]
        self.description_value.set(profile["description"])
        self.storage_value.set(
            f"Estimated storage required: {profile['estimated_gb']} GB"
        )

        self.group_list.delete(0, tk.END)
        for group in profile["groups"]:
            self.group_list.insert(tk.END, f"• {group}")

    def load_station_data(self) -> dict:
        if not STATION_FILE.exists():
            return {}
        try:
            with STATION_FILE.open("r", encoding="utf-8") as station_file:
                return json.load(station_file)
        except (OSError, json.JSONDecodeError):
            return {}

    def save_station_choice(self) -> None:
        profile_name = self.selected_profile.get()
        profile = STATION_PROFILES[profile_name]

        station_data = self.load_station_data()
        station_data["station_type"] = profile_name
        station_data["station_groups"] = profile["groups"]
        station_data["estimated_storage_gb"] = profile["estimated_gb"]

        try:
            with STATION_FILE.open("w", encoding="utf-8") as station_file:
                json.dump(station_data, station_file, indent=4)
        except OSError as error:
            messagebox.showerror(
                "Save failed",
                f"The station choice could not be saved:\n{error}",
            )
            return

        messagebox.showinfo(
            "Station saved",
            f"{profile_name} has been selected.",
        )
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    StationBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
