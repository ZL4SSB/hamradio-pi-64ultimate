from __future__ import annotations

import shutil
import subprocess
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from constants import APP_NAME, APP_VERSION, COLORS, DONATE_URL
from pages.applications_page import ApplicationsPage
from pages.dashboard_page import DashboardPage
from pages.hardware_page import HardwarePage
from pages.help_page import HelpPage
from pages.propagation_page import PropagationPage
from pages.settings_page import SettingsPage
from pages.updates_page import UpdatesPage
from pages.wpsd_page import WPSDPage
from services.command_service import CommandRunner
from ui.widgets import ToolTip
from ui.image_service import load_image


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} — Ham Shack Control Centre")
        self.geometry("1240x800")
        self.minsize(1024, 680)
        self.configure(bg=COLORS["background"])
        self._icon_image = load_image("hamradio-pi-64.png", 64, 64)
        if self._icon_image:
            try:
                self.iconphoto(True, self._icon_image)
            except tk.TclError:
                pass
        self.option_add("*Font", ("DejaVu Sans", 10))

        self._setup_style()
        self.runner = CommandRunner(self, self.log)
        self.pages = {}
        self.nav_buttons = {}
        self.nav_stripes = {}
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
            bordercolor=COLORS["border"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["panel_alt"])],
            foreground=[("readonly", COLORS["text"])],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["teal_dark"],
            troughcolor=COLORS["background"],
            bordercolor=COLORS["background"],
            arrowcolor=COLORS["text"],
        )

    def _build_shell(self) -> None:
        sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=244)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=COLORS["sidebar"])
        brand.pack(fill="x", padx=18, pady=(20, 16))

        logo = tk.Label(
            brand,
            text="HR",
            bg=COLORS["teal_dark"],
            fg="white",
            width=3,
            height=1,
            font=("DejaVu Sans", 15, "bold"),
        )
        logo.pack(side="left")

        brand_text = tk.Frame(brand, bg=COLORS["sidebar"])
        brand_text.pack(side="left", padx=(11, 0))
        tk.Label(
            brand_text,
            text="HamRadio-Pi",
            bg=COLORS["sidebar"],
            fg=COLORS["text"],
            font=("DejaVu Sans", 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            brand_text,
            text="ULTIMATE",
            bg=COLORS["sidebar"],
            fg=COLORS["teal"],
            font=("DejaVu Sans", 10, "bold"),
        ).pack(anchor="w")

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=14, pady=(0, 10))

        items = [
            ("Dashboard", "⌂", "System overview and live status"),
            ("Applications", "▦", "Install and manage radio software"),
            ("WPSD Centre", "◉", "WPSD SD-card and hotspot tools"),
            ("Hardware", "⌁", "Detect radios, SDRs and interfaces"),
            ("Propagation", "≋", "Solar and HF propagation tools"),
            ("Updates", "↻", "Check project update status"),
            ("Settings", "⚙", "Station and application settings"),
            ("Help & Logs", "?", "Command output and troubleshooting"),
        ]

        for name, icon, tooltip in items:
            row = tk.Frame(sidebar, bg=COLORS["sidebar"])
            row.pack(fill="x", padx=8, pady=2)

            stripe = tk.Frame(row, bg=COLORS["sidebar"], width=4)
            stripe.pack(side="left", fill="y")

            button = tk.Button(
                row,
                text=f"  {icon}   {name}",
                anchor="w",
                bg=COLORS["sidebar"],
                fg=COLORS["text"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground="white",
                relief="flat",
                bd=0,
                padx=10,
                pady=11,
                cursor="hand2",
                command=lambda page=name: self.show_page(page),
            )
            button.pack(side="left", fill="x", expand=True)
            button.bind("<Enter>", lambda _e, n=name: self._nav_hover(n, True), add="+")
            button.bind("<Leave>", lambda _e, n=name: self._nav_hover(n, False), add="+")
            self.nav_buttons[name] = button
            self.nav_stripes[name] = stripe

        footer = tk.Frame(sidebar, bg=COLORS["sidebar"])
        footer.pack(side="bottom", fill="x", padx=16, pady=14)
        tk.Label(
            footer,
            text=f"Version {APP_VERSION}",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("DejaVu Sans", 8),
        ).pack(anchor="w")
        tk.Label(
            footer,
            text="Ham Shack Control Centre",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("DejaVu Sans", 8),
        ).pack(anchor="w", pady=(2, 0))

        main = tk.Frame(self, bg=COLORS["background"])
        main.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(main, bg=COLORS["background_alt"], height=48)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self.page_title_var = tk.StringVar(value="Dashboard")
        tk.Label(
            topbar,
            textvariable=self.page_title_var,
            bg=COLORS["background_alt"],
            fg=COLORS["text"],
            font=("DejaVu Sans", 11, "bold"),
        ).pack(side="left", padx=18)

        self.top_logo = load_image("hamradio-pi-128.png", 72, 72)
        if self.top_logo:
            top_logo_label = tk.Label(topbar, image=self.top_logo, bg=COLORS["background_alt"])
            top_logo_label.pack(side="right", padx=(4, 12))

        donate_button = tk.Button(
            topbar, text="Donate", command=lambda: webbrowser.open(DONATE_URL),
            bg="#F4C430", fg="#111111", activebackground="#FFD95B",
            activeforeground="#111111", relief="flat", bd=0,
            padx=10, pady=5, cursor="hand2",
            font=("DejaVu Sans", 8, "bold")
        )
        donate_button.pack(side="right", padx=8)

        self.connection_label = tk.Label(
            topbar,
            text="● Ready",
            bg=COLORS["background_alt"],
            fg=COLORS["success"],
            font=("DejaVu Sans", 9, "bold"),
        )
        self.connection_label.pack(side="right", padx=18)

        host = tk.Frame(main, bg=COLORS["background"])
        host.pack(fill="both", expand=True)

        self.mascot_image = load_image("mascot.png", 220, 220)
        if self.mascot_image:
            mascot = tk.Label(main, image=self.mascot_image, bg=COLORS["background"])
            mascot.place(relx=1.0, rely=1.0, x=-18, y=-52, anchor="se")
            mascot.lift()

        status = tk.Frame(main, bg="#08111A")
        status.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            status,
            textvariable=self.status_var,
            bg="#08111A",
            fg=COLORS["muted"],
            font=("DejaVu Sans", 8),
        ).pack(side="left", padx=13, pady=7)
        tk.Label(
            status,
            text="Built for Amateur Radio",
            bg="#08111A",
            fg=COLORS["success"],
            font=("DejaVu Sans", 8, "bold"),
        ).pack(side="right", padx=13, pady=7)

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

    def _nav_hover(self, name: str, entering: bool) -> None:
        if name == self.current_page:
            return
        self.nav_buttons[name].configure(
            bg=COLORS["sidebar_hover"] if entering else COLORS["sidebar"]
        )

    def show_page(self, name: str) -> None:
        ToolTip.hide_all()
        self.current_page = name
        self.page_title_var.set(name)
        self.pages[name].tkraise()

        for page_name, button in self.nav_buttons.items():
            active = page_name == name
            button.configure(
                bg=COLORS["sidebar_hover"] if active else COLORS["sidebar"],
                fg="white" if active else COLORS["text"],
            )
            self.nav_stripes[page_name].configure(
                bg=COLORS["teal"] if active else COLORS["sidebar"]
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
        self.pages["Hardware"].scan()

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

    def package_action(self, action: str, entry) -> None:
        from services.settings_service import load_settings
        verbs = {
            "update": ("update", ["install", "--only-upgrade", "-y", entry.package]),
            "repair": ("repair", ["install", "--reinstall", "-y", entry.package]),
            "remove": ("remove", ["remove", "-y", entry.package]),
        }
        label, apt_args = verbs[action]
        if action == "remove" and load_settings().get("confirm_remove", True):
            if not messagebox.askyesno(APP_NAME, f"Remove {entry.name}?\n\nPackage: {entry.package}"):
                return
        command = ["pkexec", "apt-get", *apt_args]
        if shutil.which("pkexec") is None:
            command = ["sudo", "apt-get", *apt_args]
        self.show_page("Help & Logs")
        self.log("$ " + " ".join(command))
        self.runner.run(command, lambda rc: self._package_finished(entry.name, label, rc))

    def _package_finished(self, name: str, action: str, return_code: int) -> None:
        if return_code == 0:
            messagebox.showinfo(APP_NAME, f"{name}: {action} completed.")
            self.set_status(f"{name}: {action} completed")
        else:
            messagebox.showerror(APP_NAME, f"{name}: {action} failed. Check Help & Logs.")
            self.set_status(f"{name}: {action} failed")

    def _install_finished(self, name: str, return_code: int) -> None:
        if return_code == 0:
            messagebox.showinfo(APP_NAME, f"{name} installed successfully.")
            self.set_status(f"{name} installed")
        else:
            messagebox.showerror(APP_NAME, f"{name} installation failed. Check Help & Logs.")
            self.set_status(f"{name} installation failed")
