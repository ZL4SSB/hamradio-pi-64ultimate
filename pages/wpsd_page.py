from __future__ import annotations

import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox

from constants import COLORS, SCRIPTS_DIR
from pages.base_page import BasePage
from ui.widgets import Card, ToolTip, action_button


class WPSDPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "WPSD Centre", "Prepare, inspect and manage WPSD hotspot SD cards.")

        warning = tk.Frame(
            self.body, bg="#3A301F",
            highlightbackground=COLORS["warning"], highlightthickness=1
        )
        warning.pack(fill="x", pady=(0, 12))
        tk.Label(
            warning,
            text="Drive writing is not performed automatically. Always verify the target device before any future flash operation.",
            bg="#3A301F", fg=COLORS["warning"],
            font=("DejaVu Sans", 10, "bold"), justify="left", wraplength=880
        ).pack(anchor="w", padx=14, pady=11)

        actions = [
            ("Open existing WPSD Card Builder", "Runs scripts/wpsd-card-builder.sh", self.run_builder),
            ("Detect removable drives", "Shows block-device details in Help & Logs", self.detect_drives),
            ("Open WPSD website", "Opens the official WPSD project site", lambda: webbrowser.open("https://wpsd.radio/")),
        ]

        for title, detail, callback in actions:
            card = Card(self.body)
            card.pack(fill="x", pady=5)
            tk.Label(card, text=title, bg=COLORS["panel"], fg=COLORS["text"],
                     font=("DejaVu Sans", 12, "bold")).pack(anchor="w", padx=15, pady=(12, 3))
            tk.Label(card, text=detail, bg=COLORS["panel"], fg=COLORS["muted"],
                     font=("DejaVu Sans", 9)).pack(anchor="w", padx=15)
            button = action_button(card, title, callback, small=True)
            button.pack(anchor="w", padx=15, pady=12)
            ToolTip(button, detail)

    def run_builder(self) -> None:
        script = SCRIPTS_DIR / "wpsd-card-builder.sh"
        if not script.exists():
            messagebox.showwarning("HamRadio-Pi Ultimate", f"Script not found:\n{script}")
            return
        self.app.show_page("Help & Logs")
        self.app.log(f"$ bash {script}")
        self.app.runner.run(["bash", str(script)])

    def detect_drives(self) -> None:
        self.app.show_page("Help & Logs")
        self.app.log("$ lsblk -o NAME,PATH,SIZE,TYPE,TRAN,RM,MOUNTPOINTS,MODEL")
        self.app.runner.run([
            "lsblk", "-o", "NAME,PATH,SIZE,TYPE,TRAN,RM,MOUNTPOINTS,MODEL"
        ])
