from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from constants import COLORS
from pages.base_page import BasePage
from services.settings_service import load_settings, save_settings
from ui.widgets import Card, SectionTitle, action_button

class SettingsPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Settings", "Station identity and application preferences.")
        settings = load_settings()
        SectionTitle(self.body, "Station", "Used by propagation and future radio tools.").pack(fill="x", pady=(0, 8))
        card = Card(self.body)
        card.pack(fill="x")

        self.callsign = tk.StringVar(value=settings.get("callsign", ""))
        self.locator = tk.StringVar(value=settings.get("locator", ""))
        self.station_name = tk.StringVar(value=settings.get("station_name", ""))
        self.confirm_remove = tk.BooleanVar(value=settings.get("confirm_remove", True))

        fields = [
            ("Callsign", self.callsign, "Example: ZL4SSB"),
            ("Maidenhead locator", self.locator, "Example: RE54"),
            ("Station name", self.station_name, "Optional friendly name"),
        ]
        for row, (title, var, hint) in enumerate(fields):
            tk.Label(card, text=title, bg=COLORS["panel"], fg=COLORS["text"],
                     font=("DejaVu Sans", 10, "bold")).grid(row=row, column=0, sticky="w", padx=15, pady=11)
            tk.Entry(card, textvariable=var, bg=COLORS["panel_alt"], fg=COLORS["text"],
                     insertbackground=COLORS["text"], relief="flat", width=28).grid(
                row=row, column=1, padx=8, pady=11, ipady=6
            )
            tk.Label(card, text=hint, bg=COLORS["panel"], fg=COLORS["muted"],
                     font=("DejaVu Sans", 8)).grid(row=row, column=2, sticky="w", padx=8)

        tk.Checkbutton(card, text="Confirm before removing applications",
                       variable=self.confirm_remove, bg=COLORS["panel"], fg=COLORS["text"],
                       selectcolor=COLORS["panel_alt"], activebackground=COLORS["panel"],
                       activeforeground=COLORS["text"]).grid(
            row=3, column=0, columnspan=3, sticky="w", padx=15, pady=8
        )
        action_button(card, "Save settings", self.save).grid(
            row=4, column=0, columnspan=3, sticky="w", padx=15, pady=(5, 15)
        )

    def save(self) -> None:
        save_settings({
            "callsign": self.callsign.get().strip().upper(),
            "locator": self.locator.get().strip().upper(),
            "station_name": self.station_name.get().strip(),
            "confirm_remove": bool(self.confirm_remove.get()),
            "auto_refresh_dashboard": True,
        })
        self.app.set_status("Settings saved")
        messagebox.showinfo("HamRadio-Pi Ultimate", "Settings saved.")
