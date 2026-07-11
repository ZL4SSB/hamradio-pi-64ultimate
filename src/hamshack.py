#!/usr/bin/env python3

"""
HamRadio-Pi Ultimate
Dashboard prototype
Version 0.2.0
"""

import tkinter as tk
from tkinter import messagebox, ttk

from core.catalogue import ApplicationCatalogue, CatalogueError


class HamRadioPiApp:
    """Main HamRadio-Pi Ultimate window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate")
        self.root.geometry("900x650")
        self.root.minsize(760, 520)

        self.catalogue = ApplicationCatalogue()

        try:
            self.catalogue.load()
        except CatalogueError as error:
            messagebox.showerror(
                "Catalogue Error",
                str(error),
            )
            self.catalogue.applications = []

        self.create_interface()

    def create_interface(self) -> None:
        """Build the main dashboard interface."""

        main_frame = ttk.Frame(
            self.root,
            padding=20,
        )
        main_frame.pack(
            fill="both",
            expand=True,
        )

        title = ttk.Label(
            main_frame,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 24, "bold"),
        )
        title.pack(pady=(5, 2))

        subtitle = ttk.Label(
            main_frame,
            text="Build your station, not your software list.",
            font=("Arial", 11),
        )
        subtitle.pack(pady=(0, 20))

        summary_frame = ttk.LabelFrame(
            main_frame,
            text="Software Catalogue",
            padding=15,
        )
        summary_frame.pack(
            fill="x",
            pady=(0, 20),
        )

        application_count = self.catalogue.application_count()
        category_count = len(self.catalogue.categories())

        summary_text = (
            f"Applications available: {application_count}\n"
            f"Categories available: {category_count}"
        )

        ttk.Label(
            summary_frame,
            text=summary_text,
            font=("Arial", 12),
        ).pack(anchor="w")

        category_frame = ttk.LabelFrame(
            main_frame,
            text="Ham Radio Categories",
            padding=15,
        )
        category_frame.pack(
            fill="both",
            expand=True,
        )

        categories = self.catalogue.categories()

        if not categories:
            ttk.Label(
                category_frame,
                text="No applications were found in the catalogue.",
            ).pack(pady=20)
        else:
            for row, category in enumerate(categories):
                button = ttk.Button(
                    category_frame,
                    text=category,
                    command=lambda selected=category: (
                        self.show_category(selected)
                    ),
                )

                button.grid(
                    row=row // 2,
                    column=row % 2,
                    padx=10,
                    pady=10,
                    sticky="ew",
                )

            category_frame.columnconfigure(0, weight=1)
            category_frame.columnconfigure(1, weight=1)

        footer = ttk.Label(
            main_frame,
            text="Version 0.2.0",
            font=("Arial", 9),
        )
        footer.pack(pady=(15, 0))

    def show_category(self, category: str) -> None:
        """Display applications belonging to a category."""

        applications = self.catalogue.applications_in_category(
            category
        )

        application_names = "\n".join(
            f"• {application.get('name', 'Unknown')}"
            for application in applications
        )

        if not application_names:
            application_names = "No applications found."

        messagebox.showinfo(
            category,
            application_names,
        )


def main() -> None:
    root = tk.Tk()
    HamRadioPiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()