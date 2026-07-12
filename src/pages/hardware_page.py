from __future__ import annotations

import threading
import tkinter as tk

from constants import COLORS
from pages.base_page import BasePage
from services.hardware_service import scan_hardware
from ui.widgets import Card, ToolTip, action_button


class HardwarePage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Hardware", "Detect radios, SDR receivers, serial adapters and sound devices.")

        controls = tk.Frame(self.body, bg=COLORS["background"])
        controls.pack(fill="x", pady=(0, 10))
        button = action_button(controls, "Run hardware scan", self.scan)
        button.pack(side="left")
        ToolTip(button, "Read-only hardware scan. No settings are changed.")

        self.summary = tk.Label(
            controls, text="No scan has been run.", bg=COLORS["background"],
            fg=COLORS["muted"], font=("DejaVu Sans", 9)
        )
        self.summary.pack(side="left", padx=12)

        self.canvas = tk.Canvas(self.body, bg=COLORS["background"], highlightthickness=0)
        self.content = tk.Frame(self.canvas, bg=COLORS["background"])
        self.content.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.pack(fill="both", expand=True)

    def scan(self) -> None:
        self.app.set_status("Scanning hardware…")
        self.summary.configure(text="Scanning…", fg=COLORS["warning"])
        for child in self.content.winfo_children():
            child.destroy()

        def worker() -> None:
            items = scan_hardware()
            self.after(0, self._show_items, items)

        threading.Thread(target=worker, daemon=True).start()

    def _show_items(self, items) -> None:
        for item in items:
            card = Card(self.content)
            card.pack(fill="x", pady=5)
            tk.Label(card, text=item.name, bg=COLORS["panel"], fg=COLORS["text"],
                     font=("DejaVu Sans", 12, "bold")).pack(anchor="w", padx=15, pady=(12, 3))
            tk.Label(card, text=item.kind, bg=COLORS["panel"], fg=COLORS["teal"],
                     font=("DejaVu Sans", 8, "bold")).pack(anchor="w", padx=15)
            tk.Label(card, text=item.detail, bg=COLORS["panel"], fg=COLORS["muted"],
                     wraplength=850, justify="left", font=("DejaVu Sans Mono", 8)).pack(
                anchor="w", padx=15, pady=(5, 4)
            )
            tk.Label(card, text=f"Recommendation: {item.recommendation}",
                     bg=COLORS["panel"], fg=COLORS["success"],
                     wraplength=850, justify="left", font=("DejaVu Sans", 9)).pack(
                anchor="w", padx=15, pady=(0, 12)
            )

        self.summary.configure(text=f"{len(items)} result(s)", fg=COLORS["success"])
        self.app.dashboard.log(f"Hardware scan completed: {len(items)} result(s).")
        self.app.set_status("Hardware scan complete")
