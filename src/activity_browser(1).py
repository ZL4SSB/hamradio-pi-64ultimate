#!/usr/bin/env python3

"""Application installer for HamRadio-Pi Ultimate."""

from __future__ import annotations

import json
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


PROJECT_DIR = Path(__file__).resolve().parent.parent
ACTIVITIES_FILE = PROJECT_DIR / "src" / "data" / "activities.json"


class ApplicationInstaller:
    """Install application groups by operating activity."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Application Install")
        self.root.geometry("980x680")
        self.root.minsize(820, 560)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

        self.activities = self.load_activities()
        self.filtered: list[dict] = []

        self.search_text = tk.StringVar()
        self.category_filter = tk.StringVar(value="All Categories")

        self.name_value = tk.StringVar(value="Select an application group")
        self.category_value = tk.StringVar()
        self.storage_value = tk.StringVar()
        self.beginner_value = tk.StringVar()
        self.description_value = tk.StringVar()

        self.build_interface()
        self.refresh_list()

    @staticmethod
    def load_activities() -> list[dict]:
        if not ACTIVITIES_FILE.exists():
            return []

        try:
            with ACTIVITIES_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

        activities = data.get("activities", [])

        return [
            item
            for item in activities
            if isinstance(item, dict)
        ]

    def build_interface(self) -> None:
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 22, "bold"),
        ).pack(side="left")

        ttk.Button(
            header,
            text="Close",
            command=self.root.destroy,
        ).pack(side="right")

        ttk.Label(
            main,
            text="Application Install",
            font=("Arial", 15),
        ).pack(pady=(6, 4))

        ttk.Label(
            main,
            text="Choose what you want to do, and the required applications will be shown.",
        ).pack(pady=(0, 14))

        filters = ttk.LabelFrame(
            main,
            text="Find Application Groups",
            padding=12,
        )
        filters.pack(fill="x", pady=(0, 12))

        ttk.Label(
            filters,
            text="Search",
        ).grid(row=0, column=0, sticky="w")

        search = ttk.Entry(
            filters,
            textvariable=self.search_text,
        )
        search.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(8, 14),
        )
        search.bind(
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
                for item in self.activities
            }
        )

        category = ttk.Combobox(
            filters,
            textvariable=self.category_filter,
            state="readonly",
            values=["All Categories", *categories],
            width=24,
        )
        category.grid(
            row=0,
            column=3,
            sticky="ew",
            padx=(8, 0),
        )
        category.bind(
            "<<ComboboxSelected>>",
            lambda _event: self.refresh_list(),
        )

        filters.columnconfigure(1, weight=1)

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        left = ttk.LabelFrame(
            content,
            text="Application Groups",
            padding=10,
        )
        left.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.activity_list = tk.Listbox(
            left,
            exportselection=False,
            activestyle="dotbox",
        )
        self.activity_list.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.activity_list.bind(
            "<<ListboxSelect>>",
            self.show_selected_activity,
        )

        scrollbar = ttk.Scrollbar(
            left,
            orient="vertical",
            command=self.activity_list.yview,
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        self.activity_list.configure(
            yscrollcommand=scrollbar.set,
        )

        right = ttk.LabelFrame(
            content,
            text="Installation Details",
            padding=16,
        )
        right.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )
        right.columnconfigure(1, weight=1)

        ttk.Label(
            right,
            textvariable=self.name_value,
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 14),
        )

        self.add_row(
            right,
            1,
            "Category",
            self.category_value,
        )
        self.add_row(
            right,
            2,
            "Estimated storage",
            self.storage_value,
        )
        self.add_row(
            right,
            3,
            "Beginner friendly",
            self.beginner_value,
        )

        ttk.Label(
            right,
            text="Description",
            font=("Arial", 11, "bold"),
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(18, 6),
        )

        ttk.Label(
            right,
            textvariable=self.description_value,
            wraplength=480,
            justify="left",
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="nw",
        )

        ttk.Label(
            right,
            text="Applications to install",
            font=("Arial", 11, "bold"),
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(18, 6),
        )

        self.application_list = tk.Listbox(
            right,
            height=8,
        )
        self.application_list.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="nsew",
        )

        self.build_button = ttk.Button(
            right,
            text="Install Selected Group",
            command=self.build_selected_activity,
            state="disabled",
        )
        self.build_button.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(18, 0),
        )

        footer = ttk.Frame(main)
        footer.pack(fill="x", pady=(12, 0))

        self.count_value = tk.StringVar(
            value="0 application groups",
        )

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
    def add_row(
        parent: ttk.LabelFrame,
        row: int,
        title: str,
        variable: tk.StringVar,
    ) -> None:
        ttk.Label(
            parent,
            text=title,
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
        search = self.search_text.get().strip().lower()
        category = self.category_filter.get()
        filtered = []

        for activity in self.activities:
            activity_category = str(
                activity.get("category", "Other")
            )

            if (
                category != "All Categories"
                and activity_category != category
            ):
                continue

            searchable = " ".join(
                [
                    str(activity.get("name", "")),
                    activity_category,
                    str(activity.get("description", "")),
                    " ".join(activity.get("applications", [])),
                ]
            ).lower()

            if search and search not in searchable:
                continue

            filtered.append(activity)

        filtered.sort(
            key=lambda item: str(
                item.get("name", "")
            ).lower()
        )
        self.filtered = filtered

        self.activity_list.delete(0, tk.END)

        for activity in filtered:
            self.activity_list.insert(
                tk.END,
                f"{activity.get('name', 'Unknown')}  —  "
                f"{activity.get('category', 'Other')}",
            )

        self.count_value.set(
            f"{len(filtered)} application group"
            f"{'' if len(filtered) == 1 else 's'}"
        )

        self.clear_details()

    def selected_activity(self) -> dict | None:
        selection = self.activity_list.curselection()

        if not selection:
            return None

        index = selection[0]

        if index >= len(self.filtered):
            return None

        return self.filtered[index]

    def show_selected_activity(
        self,
        _event=None,
    ) -> None:
        activity = self.selected_activity()

        if activity is None:
            self.clear_details()
            return

        self.name_value.set(
            str(activity.get("name", "Unknown"))
        )
        self.category_value.set(
            str(activity.get("category", "Other"))
        )
        self.storage_value.set(
            f"{activity.get('estimated_gb', '?')} GB"
        )
        self.beginner_value.set(
            "Yes"
            if activity.get("beginner_friendly")
            else "No"
        )
        self.description_value.set(
            str(activity.get("description", ""))
        )

        self.application_list.delete(0, tk.END)

        for application in activity.get("applications", []):
            self.application_list.insert(
                tk.END,
                f"• {application}",
            )

        self.build_button.configure(
            state="normal",
        )

    def clear_details(self) -> None:
        self.name_value.set("Select an application group")
        self.category_value.set("")
        self.storage_value.set("")
        self.beginner_value.set("")
        self.description_value.set("")
        self.application_list.delete(0, tk.END)
        self.build_button.configure(
            state="disabled",
        )

    def build_selected_activity(self) -> None:
        activity = self.selected_activity()

        if activity is None:
            return

        packages = [
            str(package).strip()
            for package in activity.get("packages", [])
            if str(package).strip()
        ]

        if platform.system() != "Linux":
            messagebox.showinfo(
                "Application Install",
                "Application installation runs on Raspberry Pi OS.\n\n"
                "This Windows copy is for development and preview.",
            )
            return

        if not packages:
            messagebox.showerror(
                "Application Install",
                "No installable packages are defined for this group.",
            )
            return

        package_text = "\n".join(
            f"• {package}"
            for package in packages
        )

        confirmed = messagebox.askyesno(
            "Application Install",
            f"Install the software for:\n\n"
            f"{activity.get('name', 'Selected group')}\n\n"
            f"Packages:\n{package_text}",
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
                    *packages,
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
            f"{activity.get('name', 'The selected group')} is ready.",
        )


def main() -> None:
    root = tk.Tk()
    ApplicationInstaller(root)
    root.mainloop()


if __name__ == "__main__":
    main()
