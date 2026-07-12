from __future__ import annotations
import threading
import tkinter as tk
from constants import APP_VERSION, COLORS
from pages.base_page import BasePage
from services.update_service import git_status
from ui.widgets import Card, SectionTitle, action_button

class UpdatesPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Updates", "Check the project repository without changing local files.")
        SectionTitle(self.body, "Repository status", "The check performs git fetch only; it never installs automatically.").pack(fill="x", pady=(0, 8))
        card = Card(self.body)
        card.pack(fill="x")
        tk.Label(card, text=f"Installed application version: {APP_VERSION}",
                 bg=COLORS["panel"], fg=COLORS["text"],
                 font=("DejaVu Sans", 12, "bold")).pack(anchor="w", padx=15, pady=(14, 5))
        self.result = tk.Label(card, text="No update check has been run.",
                               bg=COLORS["panel"], fg=COLORS["muted"],
                               justify="left", font=("DejaVu Sans", 9))
        self.result.pack(anchor="w", padx=15)
        action_button(card, "Check repository", self.check).pack(anchor="w", padx=15, pady=14)

    def check(self) -> None:
        self.result.configure(text="Checking…", fg=COLORS["muted"])
        self.app.set_status("Checking repository…")
        def worker():
            result = git_status()
            self.after(0, self._show, result)
        threading.Thread(target=worker, daemon=True).start()

    def _show(self, result: dict) -> None:
        if not result.get("ok"):
            self.result.configure(text=result.get("message", "Unknown error"), fg=COLORS["warning"])
        else:
            text = (
                f"Branch: {result['branch']}\n"
                f"Remote updates available: {result['behind']}\n"
                f"Local commits ahead: {result['ahead']}\n"
                f"Uncommitted changes: {'Yes' if result['dirty'] else 'No'}\n"
                f"Status: {result['message']}"
            )
            colour = COLORS["success"] if result["behind"] == 0 else COLORS["warning"]
            self.result.configure(text=text, fg=colour)
        self.app.set_status("Repository check complete")
