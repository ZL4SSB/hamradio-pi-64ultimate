from __future__ import annotations
import os
import threading
import tkinter as tk
from tkinter import messagebox
from constants import APP_VERSION, COLORS
from pages.base_page import BasePage
from services.report_service import generate_system_report
from ui.widgets import SectionTitle, action_button

class HelpPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Help & Logs", "Live command output, troubleshooting and system reports.")
        controls = tk.Frame(self.body, bg=COLORS["background"])
        controls.pack(fill="x", pady=(0, 8))
        SectionTitle(controls, "Diagnostic console", f"HamRadio-Pi Ultimate {APP_VERSION}").pack(side="left")
        action_button(controls, "Generate system report", self.report, small=True).pack(side="right")
        action_button(controls, "Clear log", self.clear, small=True, secondary=True).pack(side="right", padx=8)

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

    def clear(self) -> None:
        self.output.delete("1.0", "end")
        self.output.insert("end", f"HamRadio-Pi Ultimate {APP_VERSION}\n\n")

    def report(self) -> None:
        self.app.set_status("Generating system report…")
        def worker():
            try:
                path = generate_system_report()
                self.after(0, self._report_done, path)
            except Exception as exc:
                self.after(0, messagebox.showerror, "HamRadio-Pi Ultimate", str(exc))
        threading.Thread(target=worker, daemon=True).start()

    def _report_done(self, path: str) -> None:
        self.log(f"System report created: {path}")
        self.app.set_status("System report created")
        messagebox.showinfo("HamRadio-Pi Ultimate", f"System report created:\n{path}")
