#!/usr/bin/env python3

"""
HamRadio-Pi Ultimate
Application Catalogue Window
Version 0.4.0
"""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parent.parent
APPLICATION_FILE = PROJECT_DIR / "src" / "data" / "applications.json"


class ApplicationCatalogueWindow:
    """Search, filter, inspect, install, and launch ham-radio applications."""

    def __init__(self, parent: tk.Misc | None = None) -> None:
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("HamRadio-Pi Ultimate - Application Catalogue")
        self.window.geometry("1000x680")
        self.window.minsize(850, 560)

        self.applications = self.load_applications()
        self.filtered_applications: list[dict[str, Any]] = []

        self.search_value = tk.StringVar()
        self.category_value = tk.StringVar(value="All Categories")
        self.status_value = tk.StringVar(value="All Statuses")
        self.summary_value = tk.StringVar()
        self.details_value = tk.StringVar(
            value="Select an application to view its details."
        )

        self.build_interface()
        self.refresh_table()

    @staticmethod
    def load_applications() -> list[dict[str, Any]]:
        """Load the application catalogue from JSON."""

        if not APPLICATION_FILE.exists():
            messagebox.showerror(
                "Catalogue missing",
                f"The catalogue file could not be found:\n{APPLICATION_FILE}",
            )
            return []

        try:
            with APPLICATION_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            messagebox.showerror(
                "Catalogue error",
                f"The catalogue could not be loaded:\n{error}",
            )
            return []

        applications = data.get("applications", [])
        return applications if isinstance(applications, list) else []

    def build_interface(self) -> None:
        """Build the catalogue interface."""

        main = ttk.Frame(self.window, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Application Catalogue",
            font=("Arial", 22, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main,
            text=(
                "Browse the amateur-radio software available through "
                "HamRadio-Pi Ultimate."
            ),
            font=("Arial", 10),
        ).pack(anchor="w", pady=(0, 14))

        filters = ttk.LabelFrame(main, text="Search and filter", padding=10)
        filters.pack(fill="x", pady=(0, 12))

        ttk.Label(filters, text="Search").grid(
            row=0, column=0, padx=(0, 6), pady=4, sticky="w"
        )
        search_entry = ttk.Entry(
            filters,
            textvariable=self.search_value,
            width=34,
        )
        search_entry.grid(
            row=0, column=1, padx=(0, 14), pady=4, sticky="ew"
        )
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_table())

        ttk.Label(filters, text="Category").grid(
            row=0, column=2, padx=(0, 6), pady=4, sticky="w"
        )

        categories = sorted(
            {
                str(app.get("category", "Other"))
                for app in self.applications
            }
        )

        category_box = ttk.Combobox(
            filters,
            textvariable=self.category_value,
            values=["All Categories", *categories],
            state="readonly",
            width=22,
        )
        category_box.grid(
            row=0, column=3, padx=(0, 14), pady=4, sticky="ew"
        )
        category_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_table())

        ttk.Label(filters, text="Status").grid(
            row=0, column=4, padx=(0, 6), pady=4, sticky="w"
        )

        status_box = ttk.Combobox(
            filters,
            textvariable=self.status_value,
            values=["All Statuses", "Installed", "Available"],
            state="readonly",
            width=16,
        )
        status_box.grid(row=0, column=5, pady=4, sticky="ew")
        status_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_table())

        filters.columnconfigure(1, weight=1)
        filters.columnconfigure(3, weight=1)

        body = ttk.Panedwindow(main, orient="horizontal")
        body.pack(fill="both", expand=True)

        list_frame = ttk.Frame(body)
        details_frame = ttk.LabelFrame(
            body,
            text="Application details",
            padding=12,
        )

        body.add(list_frame, weight=3)
        body.add(details_frame, weight=2)

        columns = ("name", "category", "activity", "status")

        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "name": "Application",
            "category": "Category",
            "activity": "Activity",
            "status": "Status",
        }

        widths = {
            "name": 190,
            "category": 150,
            "activity": 180,
            "status": 90,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.show_selected_details)
        self.tree.bind("<Double-1>", lambda _event: self.launch_selected())

        ttk.Label(
            details_frame,
            textvariable=self.details_value,
            wraplength=330,
            justify="left",
        ).pack(anchor="nw", fill="x")

        details_buttons = ttk.Frame(details_frame)
        details_buttons.pack(side="bottom", fill="x", pady=(14, 0))

        self.primary_button = ttk.Button(
            details_buttons,
            text="Install",
            command=self.primary_action,
            state="disabled",
        )
        self.primary_button.pack(fill="x", pady=4)

        ttk.Button(
            details_buttons,
            text="Refresh Status",
            command=self.refresh_table,
        ).pack(fill="x", pady=4)

        ttk.Label(
            main,
            textvariable=self.summary_value,
            font=("Arial", 9),
        ).pack(anchor="w", pady=(10, 0))

    @staticmethod
    def package_installed(package: str, command: str = "") -> bool:
        """Return True when the package or launch command appears installed."""

        if command and shutil.which(command.split()[0]):
            return True

        if platform.system() != "Linux" or not package:
            return False

        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Status}", package],
            capture_output=True,
            text=True,
            check=False,
        )
        return "install ok installed" in result.stdout

    def refresh_table(self) -> None:
        """Apply current filters and refresh the application table."""

        selected_name = self.get_selected_application_name()

        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_value.get().strip().lower()
        category = self.category_value.get()
        status_filter = self.status_value.get()

        self.filtered_applications = []

        for application in self.applications:
            name = str(application.get("name", "Unknown"))
            package = str(application.get("package", ""))
            command = str(application.get("command", ""))
            app_category = str(application.get("category", "Other"))
            activity = str(application.get("activity", ""))
            description = str(application.get("description", ""))

            installed = self.package_installed(package, command)
            status = "Installed" if installed else "Available"

            searchable = " ".join(
                [name, package, app_category, activity, description]
            ).lower()

            if search and search not in searchable:
                continue

            if category != "All Categories" and app_category != category:
                continue

            if status_filter != "All Statuses" and status != status_filter:
                continue

            application_copy = dict(application)
            application_copy["_installed"] = installed
            self.filtered_applications.append(application_copy)

            item_id = self.tree.insert(
                "",
                "end",
                values=(name, app_category, activity, status),
            )

            if name == selected_name:
                self.tree.selection_set(item_id)
                self.tree.focus(item_id)

        installed_count = sum(
            1 for app in self.filtered_applications if app.get("_installed")
        )

        self.summary_value.set(
            f"Showing {len(self.filtered_applications)} application(s) — "
            f"{installed_count} installed"
        )

        self.show_selected_details()

    def get_selected_application_name(self) -> str:
        selection = self.tree.selection()
        if not selection:
            return ""
        values = self.tree.item(selection[0], "values")
        return str(values[0]) if values else ""

    def selected_application(self) -> dict[str, Any] | None:
        name = self.get_selected_application_name()
        if not name:
            return None

        for application in self.filtered_applications:
            if str(application.get("name", "")) == name:
                return application

        return None

    def show_selected_details(self, _event: object | None = None) -> None:
        """Show details for the selected application."""

        application = self.selected_application()

        if not application:
            self.details_value.set(
                "Select an application to view its details."
            )
            self.primary_button.configure(text="Install", state="disabled")
            return

        installed = bool(application.get("_installed"))
        recommended = "Yes" if application.get("recommended") else "No"

        details = (
            f"{application.get('name', 'Unknown')}\n\n"
            f"Category: {application.get('category', 'Other')}\n"
            f"Activity: {application.get('activity', 'Not specified')}\n"
            f"Package: {application.get('package', 'Not specified')}\n"
            f"Recommended: {recommended}\n"
            f"Status: {'Installed' if installed else 'Available'}\n\n"
            f"{application.get('description', 'No description available.')}"
        )

        self.details_value.set(details)
        self.primary_button.configure(
            text="Launch" if installed else "Install",
            state="normal",
        )

    def primary_action(self) -> None:
        application = self.selected_application()
        if not application:
            return

        if application.get("_installed"):
            self.launch_application(application)
        else:
            self.install_application(application)

    def launch_selected(self) -> None:
        application = self.selected_application()
        if application and application.get("_installed"):
            self.launch_application(application)

    def launch_application(self, application: dict[str, Any]) -> None:
        command = str(application.get("command", "")).strip()

        if not command:
            messagebox.showinfo(
                "Launch application",
                "No launch command is defined for this application yet.",
            )
            return

        try:
            subprocess.Popen(command.split())
        except OSError as error:
            messagebox.showerror(
                "Launch failed",
                f"The application could not be started:\n{error}",
            )

    def install_application(self, application: dict[str, Any]) -> None:
        package = str(application.get("package", "")).strip()
        name = str(application.get("name", "Application"))

        if not package:
            messagebox.showinfo(
                "Install application",
                "No package name is defined for this application yet.",
            )
            return

        if platform.system() != "Linux":
            messagebox.showinfo(
                "Install application",
                (
                    f"{name} will be installed from Raspberry Pi OS "
                    f"using package:\n\n{package}\n\n"
                    "Package installation is available when this project "
                    "is run on Raspberry Pi OS."
                ),
            )
            return

        confirmed = messagebox.askyesno(
            "Install application",
            f"Install {name} using Raspberry Pi OS package '{package}'?",
        )

        if not confirmed:
            return

        terminal_commands = [
            ["x-terminal-emulator", "-e", "bash", "-lc",
             f"sudo apt update && sudo apt install -y {package}; "
             "echo; read -p 'Press ENTER to close...'"],
            ["lxterminal", "-e",
             f"bash -lc \"sudo apt update && sudo apt install -y {package}; "
             "echo; read -p 'Press ENTER to close...'\""],
        ]

        for command in terminal_commands:
            if shutil.which(command[0]):
                try:
                    subprocess.Popen(command)
                    return
                except OSError:
                    continue

        messagebox.showerror(
            "Install application",
            "A terminal application could not be found to run the installer.",
        )


def main() -> None:
    root = tk.Tk()
    ApplicationCatalogueWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
