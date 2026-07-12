from __future__ import annotations

import shutil
import tkinter as tk
from tkinter import messagebox, ttk

from constants import COLORS, DATA_DIR
from pages.base_page import BasePage
from services.application_service import is_installed, load_catalogue
from ui.widgets import Card, ToolTip, action_button


class ApplicationsPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Applications", "Browse, install and launch amateur-radio software.")

        controls = tk.Frame(self.body, bg=COLORS["background"])
        controls.pack(fill="x", pady=(0, 10))

        self.search_var = tk.StringVar()
        search = tk.Entry(
            controls, textvariable=self.search_var,
            bg=COLORS["panel_alt"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat",
            font=("DejaVu Sans", 10)
        )
        search.pack(side="left", fill="x", expand=True, ipady=9)
        search.bind("<KeyRelease>", lambda _e: self.render())

        self.category_var = tk.StringVar(value="All categories")
        self.category_box = ttk.Combobox(
            controls, textvariable=self.category_var, state="readonly", width=20
        )
        self.category_box.pack(side="left", padx=10)
        self.category_box.bind("<<ComboboxSelected>>", lambda _e: self.render())

        refresh = action_button(controls, "Refresh", self.render, small=True)
        refresh.pack(side="left")
        ToolTip(refresh, "Recheck which applications are installed.")

        self.canvas = tk.Canvas(self.body, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.body, orient="vertical", command=self.canvas.yview)
        self.content = tk.Frame(self.canvas, bg=COLORS["background"])
        self.content.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._wheel)

        self.render()

    def _wheel(self, event) -> None:
        if self.winfo_ismapped():
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def render(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()

        try:
            entries = load_catalogue(DATA_DIR / "applications.json")
        except Exception as exc:
            self.app.log(f"Application catalogue error: {exc}")
            return

        categories = ["All categories"] + sorted({entry.category for entry in entries})
        self.category_box["values"] = categories
        if self.category_var.get() not in categories:
            self.category_var.set("All categories")

        query = self.search_var.get().strip().lower()
        selected = self.category_var.get()

        filtered = [
            entry for entry in entries
            if (selected == "All categories" or entry.category == selected)
            and (
                not query
                or query in entry.name.lower()
                or query in entry.description.lower()
                or query in entry.category.lower()
            )
        ]

        for index, entry in enumerate(filtered):
            card = Card(self.content)
            card.pack(fill="x", pady=5)
            card.grid_columnconfigure(0, weight=1)

            title = entry.name + ("  ★ Recommended" if entry.recommended else "")
            tk.Label(card, text=title, bg=COLORS["panel"], fg=COLORS["text"],
                     font=("DejaVu Sans", 12, "bold")).grid(
                row=0, column=0, sticky="w", padx=15, pady=(12, 3)
            )
            tk.Label(card, text=entry.category, bg=COLORS["panel"], fg=COLORS["teal"],
                     font=("DejaVu Sans", 8, "bold")).grid(
                row=1, column=0, sticky="w", padx=15
            )
            tk.Label(card, text=entry.description, bg=COLORS["panel"], fg=COLORS["muted"],
                     wraplength=700, justify="left", font=("DejaVu Sans", 9)).grid(
                row=2, column=0, sticky="w", padx=15, pady=(4, 12)
            )

            installed = is_installed(entry)
            tk.Label(card, text="Installed" if installed else "Not installed",
                     bg=COLORS["panel"],
                     fg=COLORS["success"] if installed else COLORS["warning"],
                     font=("DejaVu Sans", 9, "bold")).grid(
                row=0, column=1, padx=12
            )

            label = "Launch" if installed else "Install"
            command = (
                lambda e=entry: self.app.launch_application(e)
                if installed
                else lambda e=entry: self.app.install_application(e)
            )
            if installed:
                callback = lambda e=entry: self.app.launch_application(e)
            else:
                callback = lambda e=entry: self.app.install_application(e)

            button = action_button(card, label, callback, small=True)
            button.grid(row=0, column=2, rowspan=3, padx=(0, 15), pady=12)
            ToolTip(button, f"{label} {entry.name}.")
