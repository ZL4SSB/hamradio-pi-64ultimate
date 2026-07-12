from __future__ import annotations
import tkinter as tk
import webbrowser
from tkinter import messagebox, filedialog
from constants import COLORS, SCRIPTS_DIR
from pages.base_page import BasePage
from ui.widgets import Card, SectionTitle, ToolTip, action_button

class WPSDPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "WPSD Centre", "Download, inspect, back up and prepare WPSD media.")
        warning = tk.Frame(self.body, bg="#3A301F",
                           highlightbackground=COLORS["warning"], highlightthickness=1)
        warning.pack(fill="x", pady=(0, 12))
        tk.Label(warning,
                 text="Safety rule: the GUI never guesses a target drive and never flashes automatically.",
                 bg="#3A301F", fg=COLORS["warning"],
                 font=("DejaVu Sans", 10, "bold")).pack(anchor="w", padx=14, pady=11)

        SectionTitle(self.body, "WPSD tools", "Use the existing builder or the safe helper scripts included with v1.0.").pack(fill="x", pady=(0, 8))
        actions = [
            ("Open WPSD download page", "Choose the correct image for your exact hotspot hardware.", lambda: webbrowser.open("https://wpsd.radio/#download-wpsd")),
            ("Detect removable drives", "Read-only lsblk report shown in Help & Logs.", self.detect_drives),
            ("Open existing card builder", "Runs scripts/wpsd-card-builder.sh.", self.run_builder),
            ("Back up a selected device", "Runs the guided backup helper in a terminal.", self.backup),
            ("Restore an image to a selected device", "Runs the guided restore helper with confirmation.", self.restore),
        ]
        for title, detail, callback in actions:
            card = Card(self.body)
            card.pack(fill="x", pady=5)
            tk.Label(card, text=title, bg=COLORS["panel"], fg=COLORS["text"],
                     font=("DejaVu Sans", 12, "bold")).pack(anchor="w", padx=15, pady=(12, 3))
            tk.Label(card, text=detail, bg=COLORS["panel"], fg=COLORS["muted"],
                     font=("DejaVu Sans", 9)).pack(anchor="w", padx=15)
            b = action_button(card, title, callback, small=True)
            b.pack(anchor="w", padx=15, pady=12)
            ToolTip(b, detail)

    def _script(self, name: str):
        script = SCRIPTS_DIR / name
        if not script.exists():
            messagebox.showwarning("HamRadio-Pi Ultimate", f"Script not found:\n{script}")
            return None
        return script

    def run_builder(self) -> None:
        script = self._script("wpsd-card-builder.sh")
        if script:
            self.app.show_page("Help & Logs")
            self.app.log(f"$ bash {script}")
            self.app.runner.run(["bash", str(script)])

    def detect_drives(self) -> None:
        self.app.show_page("Help & Logs")
        command = ["lsblk", "-o", "NAME,PATH,SIZE,FSTYPE,TYPE,TRAN,RM,MOUNTPOINTS,MODEL"]
        self.app.log("$ " + " ".join(command))
        self.app.runner.run(command)

    def backup(self) -> None:
        script = self._script("wpsd-backup.sh")
        if script:
            self.app.show_page("Help & Logs")
            self.app.runner.run(["bash", str(script)])

    def restore(self) -> None:
        script = self._script("wpsd-restore.sh")
        if script:
            self.app.show_page("Help & Logs")
            self.app.runner.run(["bash", str(script)])
