from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from constants import COLORS, DATA_DIR
from pages.base_page import BasePage
from services.application_service import is_installed, load_catalogue
from ui.widgets import Card, SectionTitle, ToolTip, action_button

class ApplicationsPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Applications", "Install, launch, repair, update or remove radio software.")
        intro = tk.Frame(self.body, bg=COLORS["background"])
        intro.pack(fill="x", pady=(0, 9))
        SectionTitle(intro, "Application manager", "Actions run through the system package manager.").pack(side="left")
        self.count_label = tk.Label(intro, text="", bg=COLORS["background"],
                                    fg=COLORS["muted"], font=("DejaVu Sans", 9, "bold"))
        self.count_label.pack(side="right")

        controls = tk.Frame(self.body, bg=COLORS["background"])
        controls.pack(fill="x", pady=(0, 10))
        search_wrap = tk.Frame(controls, bg=COLORS["panel_alt"],
                               highlightbackground=COLORS["border"], highlightthickness=1)
        search_wrap.pack(side="left", fill="x", expand=True)
        tk.Label(search_wrap, text="⌕", bg=COLORS["panel_alt"], fg=COLORS["teal"],
                 font=("DejaVu Sans", 13, "bold")).pack(side="left", padx=(10, 5))
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_wrap, textvariable=self.search_var, bg=COLORS["panel_alt"],
                         fg=COLORS["text"], insertbackground=COLORS["text"],
                         relief="flat", font=("DejaVu Sans", 10))
        entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        entry.bind("<KeyRelease>", lambda _e: self.render())

        self.category_var = tk.StringVar(value="All categories")
        self.category_box = ttk.Combobox(controls, textvariable=self.category_var,
                                         state="readonly", width=21)
        self.category_box.pack(side="left", padx=10)
        self.category_box.bind("<<ComboboxSelected>>", lambda _e: self.render())
        action_button(controls, "Refresh", self.render, small=True, secondary=True).pack(side="left")

        self.canvas = tk.Canvas(self.body, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.body, orient="vertical", command=self.canvas.yview)
        self.content = tk.Frame(self.canvas, bg=COLORS["background"])
        self.content.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window_id, width=e.width))
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
        categories = ["All categories"] + sorted({x.category for x in entries})
        self.category_box["values"] = categories
        if self.category_var.get() not in categories:
            self.category_var.set("All categories")
        query = self.search_var.get().strip().lower()
        selected = self.category_var.get()
        filtered = [
            x for x in entries
            if (selected == "All categories" or x.category == selected)
            and (not query or query in x.name.lower() or query in x.description.lower() or query in x.category.lower())
        ]
        self.count_label.configure(text=f"{len(filtered)} application(s)")
        for col in range(2):
            self.content.grid_columnconfigure(col, weight=1, uniform="appcards")

        for index, item in enumerate(filtered):
            row, col = divmod(index, 2)
            card = Card(self.content)
            card.grid(row=row, column=col, sticky="nsew", padx=(0 if col == 0 else 7, 0), pady=6)
            installed = is_installed(item)

            top = tk.Frame(card, bg=COLORS["panel"])
            top.pack(fill="x", padx=15, pady=(13, 5))
            tk.Label(top, text=item.name[:2].upper(), bg=COLORS["panel_alt"], fg=COLORS["teal"],
                     width=4, height=2, font=("DejaVu Sans", 10, "bold")).pack(side="left")
            title = tk.Frame(top, bg=COLORS["panel"])
            title.pack(side="left", padx=(10, 0), fill="x", expand=True)
            tk.Label(title, text=item.name, bg=COLORS["panel"], fg=COLORS["text"],
                     font=("DejaVu Sans", 12, "bold")).pack(anchor="w")
            tk.Label(title, text=item.category, bg=COLORS["panel"], fg=COLORS["teal"],
                     font=("DejaVu Sans", 8, "bold")).pack(anchor="w", pady=(2, 0))
            tk.Label(top, text="● Installed" if installed else "● Available",
                     bg=COLORS["panel"], fg=COLORS["success"] if installed else COLORS["warning"],
                     font=("DejaVu Sans", 8, "bold")).pack(side="right", anchor="n")

            tk.Label(card, text=item.description, bg=COLORS["panel"], fg=COLORS["muted"],
                     wraplength=410, justify="left", font=("DejaVu Sans", 9)).pack(
                anchor="w", padx=15, pady=(5, 12)
            )
            buttons = tk.Frame(card, bg=COLORS["panel"])
            buttons.pack(fill="x", padx=15, pady=(0, 13))
            if installed:
                action_button(buttons, "Launch", lambda e=item: self.app.launch_application(e), small=True).pack(side="left")
                action_button(buttons, "Update", lambda e=item: self.app.package_action("update", e), small=True, secondary=True).pack(side="left", padx=(6, 0))
                action_button(buttons, "Repair", lambda e=item: self.app.package_action("repair", e), small=True, secondary=True).pack(side="left", padx=(6, 0))
                action_button(buttons, "Remove", lambda e=item: self.app.package_action("remove", e), small=True, secondary=True).pack(side="left", padx=(6, 0))
            else:
                action_button(buttons, "Install", lambda e=item: self.app.install_application(e), small=True).pack(side="left")
            if item.recommended:
                tk.Label(buttons, text="★ Recommended", bg=COLORS["panel"], fg=COLORS["blue"],
                         font=("DejaVu Sans", 8, "bold")).pack(side="right")
