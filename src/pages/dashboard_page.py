from __future__ import annotations

import threading
import tkinter as tk

from constants import COLORS
from pages.base_page import BasePage
from services.system_service import system_snapshot
from ui.widgets import Card, MetricCard, SectionTitle, ToolTip, action_button


class DashboardPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Dashboard", "Live status for your Raspberry Pi ham shack.")

        title_row = tk.Frame(self.body, bg=COLORS["background"])
        title_row.pack(fill="x", pady=(0, 8))

        SectionTitle(
            title_row,
            "System overview",
            "Live information from this computer.",
        ).pack(side="left")

        refresh = action_button(title_row, "Refresh", self.refresh, small=True, secondary=True)
        refresh.pack(side="right")
        ToolTip(refresh, "Refresh model, temperature, memory, storage and network information.")

        grid = tk.Frame(self.body, bg=COLORS["background"])
        grid.pack(fill="x")
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1, uniform="metrics")

        self.cards = {}
        definitions = [
            ("model", "Computer", "Pi"),
            ("temperature", "CPU temperature", "°C"),
            ("memory", "Memory", "RAM"),
            ("disk", "Storage", "SSD"),
            ("network", "Network", "IP"),
            ("os", "Operating system", "OS"),
        ]
        for index, (key, title, icon) in enumerate(definitions):
            card = MetricCard(grid, title, icon)
            row, col = divmod(index, 3)
            card.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=(0 if col == 0 else 7, 0),
                pady=6,
            )
            self.cards[key] = card

        lower_title = SectionTitle(
            self.body,
            "Control centre",
            "Recent activity and context-aware guidance.",
        )
        lower_title.pack(fill="x", pady=(16, 7))

        lower = tk.Frame(self.body, bg=COLORS["background"])
        lower.pack(fill="both", expand=True)
        lower.grid_columnconfigure(0, weight=2)
        lower.grid_columnconfigure(1, weight=1)
        lower.grid_rowconfigure(0, weight=1)

        activity = Card(lower)
        activity.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        tk.Label(
            activity,
            text="Recent activity",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("DejaVu Sans", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(13, 8))

        self.output = tk.Text(
            activity,
            bg=COLORS["panel_soft"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            height=10,
            font=("DejaVu Sans Mono", 9),
            wrap="word",
            state="disabled",
        )
        self.output.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        yobbo = Card(lower)
        yobbo.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        badge = tk.Label(
            yobbo,
            text="Y",
            bg=COLORS["teal_dark"],
            fg="white",
            width=3,
            font=("DejaVu Sans", 14, "bold"),
        )
        badge.pack(anchor="w", padx=15, pady=(15, 8))

        tk.Label(
            yobbo,
            text="Shack Assistant",
            bg=COLORS["panel"],
            fg=COLORS["success"],
            font=("DejaVu Sans", 13, "bold"),
        ).pack(anchor="w", padx=15)

        self.yobbo_text = tk.Label(
            yobbo,
            text="Run a hardware scan and I’ll recommend useful software for anything I recognise.",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            justify="left",
            wraplength=290,
            font=("DejaVu Sans", 10),
        )
        self.yobbo_text.pack(anchor="w", padx=15, pady=(7, 12))

        button = action_button(yobbo, "Scan hardware", app.open_hardware_scan)
        button.pack(anchor="w", padx=15, pady=(0, 15))
        ToolTip(button, "Run a read-only scan for radio, SDR, audio and serial hardware.")

    def refresh(self) -> None:
        self.app.set_status("Refreshing dashboard…")

        def worker() -> None:
            snapshot = system_snapshot()
            self.after(0, self._apply_snapshot, snapshot)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_snapshot(self, snapshot: dict) -> None:
        for key, (value, detail) in snapshot.items():
            colour = None
            if key == "network":
                colour = COLORS["success"] if value == "Online" else COLORS["danger"]
                self.app.connection_label.configure(
                    text="● Online" if value == "Online" else "● Offline",
                    fg=colour,
                )
                self.yobbo_text.configure(
                    text=(
                        "The network is online. Propagation and update services can be used."
                        if value == "Online"
                        else "The network appears offline. Local tools will still work."
                    )
                )
            self.cards[key].set(value, detail, colour)
        self.app.set_status("Dashboard updated")

    def log(self, line: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", line + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")
