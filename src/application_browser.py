#!/usr/bin/env python3

"""Modern application browser for HamRadio-Pi Ultimate."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from ui import AppTheme, ToolTip


PROJECT_DIR = Path(__file__).resolve().parent.parent
CATALOGUE_FILE = PROJECT_DIR / "src" / "data" / "applications.json"


class ApplicationBrowser:
    """Browse, search, inspect, install, and launch applications."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Applications")
        self.root.geometry("1040x720")
        self.root.minsize(860, 600)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

        AppTheme.apply(self.root)

        self.applications = self.load_catalogue()
        self.filtered_applications: list[dict] = []
        self.tooltips: list[ToolTip] = []

        self.search_text = tk.StringVar()
        self.category_filter = tk.StringVar(value="All Categories")

        self.name_value = tk.StringVar(value="Select an application")
        self.category_value = tk.StringVar()
        self.package_value = tk.StringVar()
        self.activity_value = tk.StringVar()
        self.status_value = tk.StringVar()
        self.description_value = tk.StringVar()
        self.count_value = tk.StringVar(value="0 applications")

        self.build_interface()
        self.refresh_list()

    @staticmethod
    def load_catalogue() -> list[dict]:
        if not CATALOGUE_FILE.exists():
            return []

        try:
            with CATALOGUE_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

        applications = data.get("applications", [])
        return [item for item in applications if isinstance(item, dict)]

    def build_interface(self) -> None:
        main = ttk.Frame(self.root, padding=22, style="App.TFrame")
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main, style="App.TFrame")
        header.pack(fill="x", pady=(0, 16))

        title = ttk.Frame(header, style="App.TFrame")
        title.pack(side="left")

        ttk.Label(
            title,
            text="Applications",
            style="Header.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            title,
            text="Browse, install, and launch amateur-radio software.",
            style="Subheader.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        close_button = ttk.Button(
            header,
            text="Close",
            command=self.root.destroy,
            style="Modern.TButton",
        )
        close_button.pack(side="right")
        self.add_tooltip(close_button, "Close the Applications window.")

        filters = ttk.Frame(main, padding=16, style="Card.TFrame")
        filters.pack(fill="x", pady=(0, 14))
        filters.columnconfigure(1, weight=1)

        ttk.Label(
            filters,
            text="Search",
            style="CardLabel.TLabel",
        ).grid(row=0, column=0, sticky="w")

        search_entry = ttk.Entry(
            filters,
            textvariable=self.search_text,
            style="Modern.TEntry",
        )
        search_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(10, 18),
        )
        search_entry.bind(
            "<KeyRelease>",
            lambda _event: self.refresh_list(),
        )

        ttk.Label(
            filters,
            text="Category",
            style="CardLabel.TLabel",
        ).grid(row=0, column=2, sticky="w")

        categories = sorted(
            {str(item.get("category", "Other")) for item in self.applications}
        )

        category_box = ttk.Combobox(
            filters,
            textvariable=self.category_filter,
            state="readonly",
            values=["All Categories", *categories],
            width=24,
            style="Modern.TCombobox",
        )
        category_box.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        category_box.bind(
            "<<ComboboxSelected>>",
            lambda _event: self.refresh_list(),
        )

        content = ttk.Frame(main, style="App.TFrame")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content, padding=16, style="Card.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(
            left,
            text="Available Software",
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        list_frame = ttk.Frame(left, style="Card.TFrame")
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.application_list = tk.Listbox(
            list_frame,
            exportselection=False,
            activestyle="none",
            background=AppTheme.SURFACE_ALT,
            foreground=AppTheme.TEXT,
            selectbackground=AppTheme.ACCENT,
            selectforeground="#07120a",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
        )
        self.application_list.grid(row=0, column=0, sticky="nsew")
        self.application_list.bind(
            "<<ListboxSelect>>",
            self.show_selected_application,
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.application_list.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.application_list.configure(yscrollcommand=scrollbar.set)

        right = ttk.Frame(content, padding=20, style="Card.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.columnconfigure(1, weight=1)

        ttk.Label(
            right,
            textvariable=self.name_value,
            style="CardTitle.TLabel",
            font=("Segoe UI", 19, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        self.add_detail_row(right, 1, "Category", self.category_value)
        self.add_detail_row(right, 2, "Activity", self.activity_value)
        self.add_detail_row(right, 3, "Package", self.package_value)
        self.add_detail_row(right, 4, "Status", self.status_value)

        ttk.Label(
            right,
            text="Description",
            style="CardLabel.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(20, 7))

        ttk.Label(
            right,
            textvariable=self.description_value,
            style="CardValue.TLabel",
            wraplength=500,
            justify="left",
        ).grid(row=6, column=0, columnspan=2, sticky="nw")

        buttons = ttk.Frame(right, style="Card.TFrame")
        buttons.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(24, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        self.launch_button = ttk.Button(
            buttons,
            text="Launch",
            command=self.launch_selected,
            state="disabled",
            style="Modern.TButton",
        )
        self.launch_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.add_tooltip(
            self.launch_button,
            "Start the selected application when it is installed.",
        )

        self.install_button = ttk.Button(
            buttons,
            text="Install",
            command=self.install_selected,
            state="disabled",
            style="Accent.TButton",
        )
        self.install_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.add_tooltip(
            self.install_button,
            "Install the selected application on Raspberry Pi OS.",
        )

        footer = ttk.Frame(main, style="App.TFrame")
        footer.pack(fill="x", pady=(14, 0))

        ttk.Label(
            footer,
            textvariable=self.count_value,
            style="Footer.TLabel",
        ).pack(side="left")

        ttk.Label(
            footer,
            text="Press Esc to close",
            style="Footer.TLabel",
        ).pack(side="right")

    @staticmethod
    def add_detail_row(
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
    ) -> None:
        ttk.Label(
            parent,
            text=label,
            style="CardLabel.TLabel",
        ).grid(row=row, column=0, sticky="w", pady=6)

        ttk.Label(
            parent,
            textvariable=variable,
            style="CardValue.TLabel",
        ).grid(row=row, column=1, sticky="w", padx=(16, 0), pady=6)

    def add_tooltip(self, widget: tk.Widget, text: str) -> None:
        self.tooltips.append(ToolTip(widget, text))

    def refresh_list(self) -> None:
        search = self.search_text.get().strip().lower()
        category = self.category_filter.get()
        filtered: list[dict] = []

        for application in self.applications:
            app_category = str(application.get("category", "Other"))

            if category != "All Categories" and app_category != category:
                continue

            searchable = " ".join(
                [
                    str(application.get("name", "")),
                    app_category,
                    str(application.get("activity", "")),
                    str(application.get("description", "")),
                    str(application.get("package", "")),
                ]
            ).lower()

            if search and search not in searchable:
                continue

            filtered.append(application)

        filtered.sort(key=lambda item: str(item.get("name", "")).lower())
        self.filtered_applications = filtered
        self.application_list.delete(0, tk.END)

        for application in filtered:
            name = str(application.get("name", "Unknown"))
            category_name = str(application.get("category", "Other"))
            self.application_list.insert(tk.END, f"{name}  ·  {category_name}")

        self.count_value.set(
            f"{len(filtered)} application{'' if len(filtered) == 1 else 's'}"
        )
        self.clear_details()

    def selected_application(self) -> dict | None:
        selection = self.application_list.curselection()
        if not selection:
            return None

        index = selection[0]
        if index >= len(self.filtered_applications):
            return None

        return self.filtered_applications[index]

    def show_selected_application(self, _event=None) -> None:
        application = self.selected_application()

        if application is None:
            self.clear_details()
            return

        installed = self.is_installed(application)

        self.name_value.set(str(application.get("name", "Unknown")))
        self.category_value.set(str(application.get("category", "Other")))
        self.activity_value.set(str(application.get("activity", "")))
        self.package_value.set(str(application.get("package", "")) or "Not specified")
        self.description_value.set(str(application.get("description", "")))
        self.status_value.set("Installed" if installed else "Not installed")

        self.launch_button.configure(
            state="normal" if installed else "disabled"
        )
        self.install_button.configure(
            state=(
                "normal"
                if not installed and platform.system() == "Linux"
                else "disabled"
            )
        )

    def clear_details(self) -> None:
        self.name_value.set("Select an application")
        self.category_value.set("")
        self.activity_value.set("")
        self.package_value.set("")
        self.status_value.set("")
        self.description_value.set("")
        self.launch_button.configure(state="disabled")
        self.install_button.configure(state="disabled")

    @staticmethod
    def is_installed(application: dict) -> bool:
        command = str(
            application.get("command")
            or application.get("package")
            or ""
        ).strip()
        return bool(command and shutil.which(command))

    def launch_selected(self) -> None:
        application = self.selected_application()
        if application is None:
            return

        command = str(
            application.get("command")
            or application.get("package")
            or ""
        ).strip()

        try:
            subprocess.Popen([command])
        except OSError as error:
            messagebox.showerror("Launch failed", str(error))

    def install_selected(self) -> None:
        application = self.selected_application()
        if application is None:
            return

        package = str(application.get("package", "")).strip()
        if not package:
            messagebox.showerror(
                "Install application",
                "No Debian package is configured for this application.",
            )
            return

        confirmed = messagebox.askyesno(
            "Install application",
            f"Install {application.get('name', package)}?\n\nPackage: {package}",
        )
        if not confirmed:
            return

        try:
            result = subprocess.run(
                ["pkexec", "apt-get", "install", "-y", package],
                text=True,
                capture_output=True,
                check=False,
            )
        except OSError as error:
            messagebox.showerror("Installation failed", str(error))
            return

        if result.returncode != 0:
            messagebox.showerror(
                "Installation failed",
                result.stderr.strip()
                or result.stdout.strip()
                or "The package installer returned an error.",
            )
            return

        messagebox.showinfo(
            "Installation complete",
            f"{application.get('name', package)} was installed.",
        )
        self.show_selected_application()


def main() -> None:
    root = tk.Tk()
    ApplicationBrowser(root)
    root.mainloop()


if __name__ == "__main__":
    main()
