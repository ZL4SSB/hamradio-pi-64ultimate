from __future__ import annotations

import json
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from constants import APP_VERSION, BASE_DIR, COLORS, CONFIG_DIR
from pages.base_page import BasePage
from ui.widgets import Card, action_button


class PropagationPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Propagation", "Foundation for solar, band-condition and grey-line tools.")
        card = Card(self.body)
        card.pack(fill="x")
        tk.Label(
            card,
            text="Live propagation data will be added after the core installer and hardware systems are stable.",
            bg=COLORS["panel"], fg=COLORS["muted"],
            font=("DejaVu Sans", 10), wraplength=860, justify="left"
        ).pack(anchor="w", padx=15, pady=15)


class UpdatesPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Updates", "Read-only Git update status.")
        card = Card(self.body)
        card.pack(fill="x")
        tk.Label(card, text=f"Installed version: {APP_VERSION}",
                 bg=COLORS["panel"], fg=COLORS["text"],
                 font=("DejaVu Sans", 12, "bold")).pack(anchor="w", padx=15, pady=(14, 5))
        self.result = tk.Label(card, text="No update check has been run.",
                               bg=COLORS["panel"], fg=COLORS["muted"],
                               font=("DejaVu Sans", 9), justify="left")
        self.result.pack(anchor="w", padx=15)
        action_button(card, "Check repository", self.check).pack(anchor="w", padx=15, pady=14)

    def check(self) -> None:
        if not (BASE_DIR / ".git").exists():
            self.result.configure(text="This directory is not a Git working copy.", fg=COLORS["warning"])
            return
        self.result.configure(text="Checking…", fg=COLORS["muted"])

        def worker() -> None:
            try:
                subprocess.run(["git", "-C", str(BASE_DIR), "fetch", "--quiet"], timeout=30, check=True)
                result = subprocess.run(
                    ["git", "-C", str(BASE_DIR), "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode:
                    text = result.stderr.strip() or "No upstream branch configured."
                    colour = COLORS["warning"]
                else:
                    ahead, behind = result.stdout.strip().split()
                    text = f"Local commits ahead: {ahead}\nRemote commits available: {behind}"
                    colour = COLORS["success"] if behind == "0" else COLORS["warning"]
            except Exception as exc:
                text = f"Update check failed: {exc}"
                colour = COLORS["danger"]
            self.after(0, lambda: self.result.configure(text=text, fg=colour))

        threading.Thread(target=worker, daemon=True).start()


class SettingsPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Settings", "Station identity and preferences.")
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        current = self._load()

        card = Card(self.body)
        card.pack(fill="x")
        self.callsign = tk.StringVar(value=current.get("callsign", ""))
        self.locator = tk.StringVar(value=current.get("locator", ""))

        for row, (title, var, hint) in enumerate([
            ("Callsign", self.callsign, "Example: ZL4SSB"),
            ("Maidenhead locator", self.locator, "Example: RE54"),
        ]):
            tk.Label(card, text=title, bg=COLORS["panel"], fg=COLORS["text"],
                     font=("DejaVu Sans", 10, "bold")).grid(row=row, column=0, sticky="w", padx=15, pady=12)
            tk.Entry(card, textvariable=var, bg=COLORS["panel_alt"], fg=COLORS["text"],
                     insertbackground=COLORS["text"], relief="flat", width=25).grid(
                row=row, column=1, padx=8, pady=12, ipady=6
            )
            tk.Label(card, text=hint, bg=COLORS["panel"], fg=COLORS["muted"],
                     font=("DejaVu Sans", 8)).grid(row=row, column=2, sticky="w", padx=8)

        action_button(card, "Save settings", self.save).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=15, pady=(4, 15)
        )

    def _load(self) -> dict:
        try:
            return json.loads((CONFIG_DIR / "settings.json").read_text())
        except Exception:
            return {}

    def save(self) -> None:
        settings = {
            "callsign": self.callsign.get().strip().upper(),
            "locator": self.locator.get().strip().upper(),
        }
        (CONFIG_DIR / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
        self.app.set_status("Settings saved")
        messagebox.showinfo("HamRadio-Pi Ultimate", "Settings saved.")


class HelpPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Help & Logs", "Live command output and troubleshooting.")
        self.output = tk.Text(
            self.body, bg=COLORS["panel"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat",
            font=("DejaVu Sans Mono", 9), wrap="word"
        )
        self.output.pack(fill="both", expand=True)
        self.output.insert("end", f"HamRadio-Pi Ultimate {APP_VERSION}\n\n")

    def log(self, line: str) -> None:
        self.output.insert("end", line + "\n")
        self.output.see("end")
