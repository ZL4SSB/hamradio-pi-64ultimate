from __future__ import annotations

import json
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

from constants import APP_NAME, APP_VERSION, COLORS
from pages.applications_page import ApplicationsPage
from pages.dashboard_page import DashboardPage
from pages.hardware_page import HardwarePage
from pages.simple_pages import HelpPage, PropagationPage, SettingsPage, UpdatesPage
from pages.wpsd_page import WPSDPage
from services.command_service import CommandRunner


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} — Ham Shack Control Centre")
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.configure(bg=COLORS["background"])
        self.option_add("*Font", ("DejaVu Sans", 10))

        self._setup_style()
        self.runner = CommandRunner(self, self.log)
        self.pages = {}
        self.nav_buttons = {}
        self.current_page = ""

        self._build_shell()
        self.show_page("Dashboard")
        self.dashboard.refresh()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["panel_alt"],
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["teal_dark"],
            troughcolor=COLORS["background"],
            bordercolor=COLORS["background"],
            arrowcolor=COLORS["text"],
        )

    def _build_shell(self) -> None:
        sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=COLORS["sidebar"])
        brand.pack(fill="x", padx=17, pady=(20, 17))
        tk.Label(brand, text="HamRadio-Pi", bg=COLORS["sidebar"], fg=COLORS["text"],
                 font=("DejaVu Sans", 16, "bold")).pack(anchor="w")
        tk.Label(brand, text="ULTIMATE", bg=COLORS["sidebar"], fg=COLORS["teal"],
                 font=("DejaVu Sans", 12, "bold")).pack(anchor="w")
        tk.Label(brand, text="Ham Shack Control Centre", bg=COLORS["sidebar"], fg=COLORS["muted"],
                 font=("DejaVu Sans", 8)).pack(anchor="w", pady=(3, 0))

        items = [
            ("Dashboard", "⌂"),
            ("Applications", "▦"),
            ("WPSD Centre", "◉"),
            ("Hardware", "⌁"),
            ("Propagation", "≋"),
            ("Updates", "↻"),
            ("Settings", "⚙"),
            ("Help & Logs", "?"),
        ]
        for name, icon in items:
            button = tk.Button(
                sidebar, text=f"  {icon}   {name}", anchor="w",
                bg=COLORS["sidebar"], fg=COLORS["text"],
                activebackground=COLORS["teal_dark"], activeforeground="white",
                relief="flat", bd=0, padx=13, pady=11, cursor="hand2",
                command=lambda page=name: self.show_page(page)
            )
            button.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[name] = button

        tk.Label(sidebar, text=f"Version {APP_VERSION}", bg=COLORS["sidebar"],
                 fg=COLORS["muted"], font=("DejaVu Sans", 8)).pack(
            side="bottom", anchor="w", padx=18, pady=16
        )

        main = tk.Frame(self, bg=COLORS["background"])
        main.pack(side="left", fill="both", expand=True)

        host = tk.Frame(main, bg=COLORS["background"])
        host.pack(fill="both", expand=True)

        status = tk.Frame(main, bg="#09111B")
        status.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(status, textvariable=self.status_var, bg="#09111B", fg=COLORS["muted"],
                 font=("DejaVu Sans", 8)).pack(side="left", padx=13, pady=7)
        tk.Label(status, text="73 mate!", bg="#09111B", fg=COLORS["success"],
                 font=("DejaVu Sans", 8, "bold")).pack(side="right", padx=13, pady=7)

        self.dashboard = DashboardPage(host, self)
        page_map = {
            "Dashboard": self.dashboard,
            "Applications": ApplicationsPage(host, self),
            "WPSD Centre": WPSDPage(host, self),
            "Hardware": HardwarePage(host, self),
            "Propagation": PropagationPage(host, self),
            "Updates": UpdatesPage(host, self),
            "Settings": SettingsPage(host, self),
            "Help & Logs": HelpPage(host, self),
        }

        for name, page in page_map.items():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[name] = page

    def show_page(self, name: str) -> None:
        self.current_page = name
        self.pages[name].tkraise()
        for page_name, button in self.nav_buttons.items():
            button.configure(
                bg=COLORS["teal_dark"] if page_name == name else COLORS["sidebar"],
                fg="white" if page_name == name else COLORS["text"],
            )
        self.set_status(name)

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def log(self, line: str) -> None:
        page = self.pages.get("Help & Logs")
        if isinstance(page, HelpPage):
            page.log(line)
        self.dashboard.log(line)

    def open_hardware_scan(self) -> None:
        self.show_page("Hardware")
        page = self.pages["Hardware"]
        page.scan()

    def launch_application(self, entry) -> None:
        try:
            subprocess.Popen([entry.command], start_new_session=True)
            self.set_status(f"Launched {entry.name}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not launch {entry.name}:\n{exc}")

    def install_application(self, entry) -> None:
        if not messagebox.askyesno(
            APP_NAME,
            f"Install {entry.name}?\n\nPackage: {entry.package}\n\n"
            "The package manager may ask for your password."
        ):
            return

        command = ["pkexec", "apt-get", "install", "-y", entry.package]
        if shutil.which("pkexec") is None:
            command = ["sudo", "apt-get", "install", "-y", entry.package]

        self.show_page("Help & Logs")
        self.log("$ " + " ".join(command))
        self.runner.run(command, lambda rc: self._install_finished(entry.name, rc))

    def _install_finished(self, name: str, return_code: int) -> None:
        if return_code == 0:
            messagebox.showinfo(APP_NAME, f"{name} installed successfully.")
            self.set_status(f"{name} installed")
        else:
            messagebox.showerror(APP_NAME, f"{name} installation failed. Check Help & Logs.")
            self.set_status(f"{name} installation failed")
