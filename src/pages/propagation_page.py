from __future__ import annotations
import threading
import tkinter as tk
from constants import COLORS
from pages.base_page import BasePage
from services.propagation_service import fetch_snapshot
from ui.widgets import MetricCard, SectionTitle, ToolTip, action_button, Card

class PropagationPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Propagation", "Live solar and geomagnetic data from NOAA SWPC.")

        row = tk.Frame(self.body, bg=COLORS["background"])
        row.pack(fill="x", pady=(0, 8))
        SectionTitle(row, "Space weather", "Live values are fetched only when you press Refresh.").pack(side="left")
        refresh = action_button(row, "Refresh propagation", self.refresh, small=True)
        refresh.pack(side="right")
        ToolTip(refresh, "Fetch current solar and geomagnetic values from NOAA SWPC.")

        grid = tk.Frame(self.body, bg=COLORS["background"])
        grid.pack(fill="x")
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1, uniform="prop")
        defs = [
            ("solar_flux", "10.7 cm solar flux", "SFI"),
            ("k_index", "Planetary K-index", "Kp"),
            ("solar_wind", "Solar wind speed", "SW"),
            ("r_scale", "Radio blackout scale", "R"),
            ("s_scale", "Solar radiation scale", "S"),
            ("g_scale", "Geomagnetic storm scale", "G"),
        ]
        self.cards = {}
        for i, (key, title, icon) in enumerate(defs):
            card = MetricCard(grid, title, icon)
            r, c = divmod(i, 3)
            card.grid(row=r, column=c, sticky="nsew", padx=(0 if c == 0 else 7, 0), pady=6)
            self.cards[key] = card

        SectionTitle(self.body, "Band guidance", "General guidance only; local paths can differ.").pack(fill="x", pady=(16, 7))
        self.band_card = Card(self.body)
        self.band_card.pack(fill="both", expand=True)
        self.band_labels = {}
        for i, band in enumerate(("80m", "40m", "20m", "15m", "10m")):
            frame = tk.Frame(self.band_card, bg=COLORS["panel"])
            frame.pack(fill="x", padx=15, pady=(12 if i == 0 else 3, 12 if i == 4 else 3))
            tk.Label(frame, text=band, width=5, bg=COLORS["panel_alt"], fg=COLORS["teal"],
                     font=("DejaVu Sans", 10, "bold"), pady=5).pack(side="left")
            label = tk.Label(frame, text="Press Refresh to load conditions.",
                             bg=COLORS["panel"], fg=COLORS["muted"],
                             font=("DejaVu Sans", 9))
            label.pack(side="left", padx=12)
            self.band_labels[band] = label

        self.updated_label = tk.Label(self.body, text="", bg=COLORS["background"],
                                      fg=COLORS["muted"], font=("DejaVu Sans", 8))
        self.updated_label.pack(anchor="e", pady=(7, 0))

    def refresh(self) -> None:
        self.app.set_status("Fetching propagation data…")
        def worker():
            snapshot = fetch_snapshot()
            self.after(0, self._apply, snapshot)
        threading.Thread(target=worker, daemon=True).start()

    def _apply(self, data: dict) -> None:
        details = {
            "solar_flux": "Solar activity indicator",
            "k_index": "0 quiet · 5 storm threshold",
            "solar_wind": "km/s",
            "r_scale": "R0–R5",
            "s_scale": "S0–S5",
            "g_scale": "G0–G5",
        }
        for key, card in self.cards.items():
            value = str(data.get(key, "—"))
            colour = COLORS["text"]
            if key in ("r_scale", "s_scale", "g_scale") and value not in ("0", "—"):
                colour = COLORS["warning"]
            card.set(value, details[key], colour)
        for band, text in data.get("bands", {}).items():
            self.band_labels[band].configure(text=text, fg=COLORS["text"])
        self.updated_label.configure(text=f"Updated: {data.get('updated', '')}")
        if data.get("errors"):
            self.app.log("Propagation warnings: " + " | ".join(data["errors"]))
        self.app.set_status("Propagation data updated")
