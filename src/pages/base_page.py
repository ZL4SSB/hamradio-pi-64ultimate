import tkinter as tk

from constants import COLORS


class BasePage(tk.Frame):
    def __init__(self, parent, app, title: str, subtitle: str) -> None:
        super().__init__(parent, bg=COLORS["background"])
        self.app = app

        header = tk.Frame(self, bg=COLORS["background"])
        header.pack(fill="x", padx=28, pady=(23, 12))

        tk.Label(
            header, text=title, bg=COLORS["background"], fg=COLORS["text"],
            font=("DejaVu Sans", 22, "bold")
        ).pack(anchor="w")
        tk.Label(
            header, text=subtitle, bg=COLORS["background"], fg=COLORS["muted"],
            font=("DejaVu Sans", 10)
        ).pack(anchor="w", pady=(3, 0))

        self.body = tk.Frame(self, bg=COLORS["background"])
        self.body.pack(fill="both", expand=True, padx=28, pady=(0, 22))
