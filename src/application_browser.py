#!/usr/bin/env python3

"""Searchable application browser for HamRadio-Pi Ultimate."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


PROJECT_DIR = Path(__file__).resolve().parent.parent
CATALOGUE_FILE = PROJECT_DIR / "src" / "data" / "applications.json"


class ApplicationBrowser:
    """Browse, search, and inspect catalogue applications."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Applications")
        self.root.geometry("980x680")
        self.root.minsize(820, 560)

        self.applications = self.load_catalogue()
        self.filtered_applications: list[dict] = []

        self.search_text = tk.StringVar()
        self.category_filter = tk.StringVar(value="All Categories")

        self.name_value = tk.StringVar(value="Select an application")
        self.category_value = tk.StringVar(value="")
        self.package_value = tk.StringVar(value="")
        self.activity_value = tk.StringVar(value="")
        self.status_value = tk.StringVar(value="")
        self.description_value = tk.StringVar(value="")

        self.build_interface()
        self.refresh_list()

    @staticmethod
    def load_catalogue() -> list[dict]:
        """Load applications from the project catalogue."""

        if not CATALOGUE_FILE.exists():
            return []

        try:
            with CATALOGUE_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

        applications = data.get("applications", [])

        if not isinstance(applications, list):
            return []

        return [
            item
            for item in applications
            if isinstance(item, dict)
        ]

    def build_interface(self) -> None:
        """Create the application browser interface."""

        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 22, "bold"),
        ).pack()

        ttk.Label(
            main,
            text="Application Browser",
            font=("Arial", 15),
        ).pack(pady=(2, 14))

        filters = ttk.LabelFrame(
            main,
            text="Find Applications",
            padding=12,
        )
        filters.pack(fill="x", pady=(0, 12))

        ttk.Label(
            filters,
            text="Search",
        ).grid(row=0, column=0, sticky="w")

        search_entry = ttk.Entry(
            filters,
            textvariable=self.search_text,
        )
        search_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(8, 14),
        )
        search_entry.bind(
            "<KeyRelease>",
            lambda _event: self.refresh_list(),
        )

        ttk.Label(
            filters,
            text="Category",
        ).grid(row=0, column=2, sticky="w")

        categories = sorted(
            {
                str(item.get("category", "Other"))
                for item in self.applications
            }
        )

        category_box = ttk.Combobox(
            filters,
            textvariable=self.category_filter,
            state="readonly",
            values=["All Categories", *categories],
            width=24,
        )
        category_box.grid(
            row=0,
            column=3,
            sticky="ew",
            padx=(8, 0),
        )
        category_box.bind(
            "<<ComboboxSelected>>",
            lambda _event: self.refresh_list(),
        )

        filters.columnconfigure(1, weight=1)

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(
            content,
            text="Applications",
            padding=10,
        )
        list_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.application_list = tk.Listbox(
            list_frame,
            activestyle="dotbox",
            exportselection=False,
        )
        self.application_list.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.application_list.bind(
            "<<ListboxSelect>>",
            self.show_selected_application,
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.application_list.yview,
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        self.application_list.configure(
            yscrollcommand=scrollbar.set,
        )

        details = ttk.LabelFrame(
            content,
            text="Application Details",
            padding=16,
        )
        details.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )
        details.columnconfigure(1, weight=1)

        ttk.Label(
            details,
            textvariable=self.name_value,
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 14),
        )

        self.add_detail_row(
            details,
            1,
            "Category",
            self.category_value,
        )
        self.add_detail_row(
            details,
            2,
            "Activity",
            self.activity_value,
        )
        self.add_detail_row(
            details,
            3,
            "Package",
            self.package_value,
        )
        self.add_detail_row(
            details,
            4,
            "Status",
            self.status_value,
        )

        ttk.Label(
            details,
            text="Description",
            font=("Arial", 11, "bold"),
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(18, 6),
        )

        ttk.Label(
            details,
            textvariable=self.description_value,
            wraplength=480,
            justify="left",
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="nw",
        )

        button_frame = ttk.Frame(details)
        button_frame.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(24, 0),
        )
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.launch_button = ttk.Button(
            button_frame,
            text="Launch",
            command=self.launch_selected,
            state="disabled",
        )
        self.launch_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6),
        )

        self.install_button = ttk.Button(
            button_frame,
            text="Install",
            command=self.install_selected,
            state="disabled",
        )
        self.install_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

        footer = ttk.Frame(main)
        footer.pack(fill="x", pady=(12, 0))

        self.count_value = tk.StringVar(value="0 applications")
        ttk.Label(
            footer,
            textvariable=self.count_value,
        ).pack(side="left")

        ttk.Button(
            footer,
            text="Close",
            command=self.root.destroy,
        ).pack(side="right")

    @staticmethod
    def add_detail_row(
        parent: ttk.LabelFrame,
        row: int,
        label: str,
        variable: tk.StringVar,
    ) -> None:
        """Add one field to the details panel."""

        ttk.Label(
            parent,
            text=label,
            font=("Arial", 11, "bold"),
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=5,
        )

        ttk.Label(
            parent,
            textvariable=variable,
        ).grid(
            row=row,
            column=1,
            sticky="w",
            padx=(14, 0),
            pady=5,
        )

    def refresh_list(self) -> None:
        """Apply search and category filters."""

        search = self.search_text.get().strip().lower()
        category = self.category_filter.get()

        filtered: list[dict] = []

        for application in self.applications:
            app_category = str(
                application.get("category", "Other")
            )

            if (
                category != "All Categories"
                and app_category != category
            ):
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

        filtered.sort(
            key=lambda item: str(
                item.get("name", "")
            ).lower()
        )

        self.filtered_applications = filtered
        self.application_list.delete(0, tk.END)

        for application in filtered:
            name = str(application.get("name", "Unknown"))
            category_name = str(
                application.get("category", "Other")
            )
            self.application_list.insert(
                tk.END,
                f"{name}  —  {category_name}",
            )

        self.count_value.set(
            f"{len(filtered)} application"
            f"{'' if len(filtered) == 1 else 's'}"
        )

        self.clear_details()

    def selected_application(self) -> dict | None:
        """Return the currently selected catalogue entry."""

        selection = self.application_list.curselection()

        if not selection:
            return None

        index = selection[0]

        if index >= len(self.filtered_applications):
            return None

        return self.filtered_applications[index]

    def show_selected_application(self, _event=None) -> None:
        """Display details for the selected application."""

        application = self.selected_application()

        if application is None:
            self.clear_details()
            return

        name = str(application.get("name", "Unknown"))
        package = str(application.get("package", ""))
        installed = self.is_installed(application)

        self.name_value.set(name)
        self.category_value.set(
            str(application.get("category", "Other"))
        )
        self.activity_value.set(
            str(application.get("activity", ""))
        )
        self.package_value.set(package or "Not specified")
        self.description_value.set(
            str(application.get("description", ""))
        )
        self.status_value.set(
            "Installed" if installed else "Not installed"
        )

        self.launch_button.configure(
            state="normal" if installed else "disabled"
        )
        self.install_button.configure(
            state=(
                "disabled"
                if installed or platform.system() != "Linux"
                else "normal"
            )
        )

    def clear_details(self) -> None:
        """Reset the application details panel."""

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
        """Check whether an application command is currently available."""

        command = str(
            application.get("command")
            or application.get("package")
            or ""
        ).strip()

        if not command:
            return False

        return shutil.which(command) is not None

    def launch_selected(self) -> None:
        """Launch the selected installed application."""

        application = self.selected_application()

        if application is None:
            return

        command = str(
            application.get("command")
            or application.get("package")
            or ""
        ).strip()

        if not command:
            messagebox.showerror(
                "Launch failed",
                "No launch command is configured for this application.",
            )
            return

        try:
            subprocess.Popen([command])
        except OSError as error:
            messagebox.showerror(
                "Launch failed",
                str(error),
            )

    def install_selected(self) -> None:
        """Install the selected package on Raspberry Pi OS."""

        application = self.selected_application()

        if application is None:
            return

        if platform.system() != "Linux":
            messagebox.showinfo(
                "Install application",
                "Application installation is only available on "
                "Raspberry Pi OS.",
            )
            return

        package = str(
            application.get("package", "")
        ).strip()

        if not package:
            messagebox.showerror(
                "Install application",
                "No Debian package is configured for this application.",
            )
            return

        confirmed = messagebox.askyesno(
            "Install application",
            f"Install {application.get('name', package)}?\n\n"
            f"Package: {package}",
        )

        if not confirmed:
            return

        try:
            result = subprocess.run(
                [
                    "pkexec",
                    "apt-get",
                    "install",
                    "-y",
                    package,
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        except OSError as error:
            messagebox.showerror(
                "Installation failed",
                str(error),
            )
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
