from __future__ import annotations

import threading
import tkinter as tk

from constants import COLORS
from pages.base_page import BasePage
from services.hardware_service import scan_hardware
from ui.widgets import Card, SectionTitle, ToolTip, action_button


class HardwarePage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Hardware", "Detect radios, SDR receivers, serial adapters and sound devices.")

        heading = tk.Frame(self.body, bg=COLORS["background"])
        heading.pack(fill="x", pady=(0, 9))

        SectionTitle(
            heading,
            "Hardware discovery",
            "The scan is read-only and will not alter device settings.",
        ).pack(side="left")

        self.summary = tk.Label(
            heading,
            text="No scan has been run.",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("DejaVu Sans", 9, "bold"),
        )
        self.summary.pack(side="right")

        controls = tk.Frame(self.body, bg=COLORS["background"])
        controls.pack(fill="x", pady=(0, 10))

        button = action_button(controls, "Run hardware scan", self.scan)
        button.pack(side="left")
        ToolTip(button, "Scan USB, serial and audio devices without changing them.")

        clear = action_button(controls, "Clear results", self.clear, small=True, secondary=True)
        clear.pack(side="left", padx=(8, 0))

        self.canvas = tk.Canvas(self.body, bg=COLORS["background"], highlightthickness=0)
        self.content = tk.Frame(self.canvas, bg=COLORS["background"])
        self.content.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.window_id, width=e.width),
        )
        self.canvas.pack(fill="both", expand=True)

    def clear(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()
        self.summary.configure(text="No scan has been run.", fg=COLORS["muted"])
        self.app.set_status("Hardware results cleared")

    def scan(self) -> None:
        self.app.set_status("Scanning hardware…")
        self.summary.configure(text="Scanning…", fg=COLORS["warning"])

        for child in self.content.winfo_children():
            child.destroy()

        loading = Card(self.content)
        loading.pack(fill="x", pady=5)
        tk.Label(
            loading,
            text="Scanning USB, serial and audio devices…",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("DejaVu Sans", 10),
        ).pack(anchor="w", padx=15, pady=15)

        def worker() -> None:
            items = scan_hardware()
            self.after(0, self._show_items, items)

        threading.Thread(target=worker, daemon=True).start()

    def _show_items(self, items) -> None:
        for child in self.content.winfo_children():
            child.destroy()

        for item in items:
            card = Card(self.content)
            card.pack(fill="x", pady=5)

            top = tk.Frame(card, bg=COLORS["panel"])
            top.pack(fill="x", padx=15, pady=(13, 5))

            badge_text = {
                "SDR": "SDR",
                "CAT / Serial": "CAT",
                "Audio": "AUD",
                "Navigation": "GPS",
                "Information": "INFO",
            }.get(item.kind, "HW")

            tk.Label(
                top,
                text=badge_text,
                bg=COLORS["panel_alt"],
                fg=COLORS["teal"],
                width=5,
                height=2,
                font=("DejaVu Sans", 9, "bold"),
            ).pack(side="left")

            info = tk.Frame(top, bg=COLORS["panel"])
            info.pack(side="left", padx=(10, 0), fill="x", expand=True)

            tk.Label(
                info,
                text=item.name,
                bg=COLORS["panel"],
                fg=COLORS["text"],
                font=("DejaVu Sans", 12, "bold"),
            ).pack(anchor="w")

            tk.Label(
                info,
                text=item.kind,
                bg=COLORS["panel"],
                fg=COLORS["teal"],
                font=("DejaVu Sans", 8, "bold"),
            ).pack(anchor="w", pady=(2, 0))

            tk.Label(
                card,
                text=item.detail,
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                wraplength=900,
                justify="left",
                font=("DejaVu Sans Mono", 8),
            ).pack(anchor="w", padx=15, pady=(5, 4))

            rec = tk.Frame(card, bg=COLORS["panel_soft"])
            rec.pack(fill="x", padx=15, pady=(5, 13))
            tk.Label(
                rec,
                text="Recommended",
                bg=COLORS["panel_soft"],
                fg=COLORS["success"],
                font=("DejaVu Sans", 8, "bold"),
            ).pack(anchor="w", padx=10, pady=(8, 2))
            tk.Label(
                rec,
                text=item.recommendation,
                bg=COLORS["panel_soft"],
                fg=COLORS["text"],
                wraplength=850,
                justify="left",
                font=("DejaVu Sans", 9),
            ).pack(anchor="w", padx=10, pady=(0, 8))

        self.summary.configure(text=f"{len(items)} result(s)", fg=COLORS["success"])
        self.app.dashboard.log(f"Hardware scan completed: {len(items)} result(s).")
        self.app.set_status("Hardware scan complete")
