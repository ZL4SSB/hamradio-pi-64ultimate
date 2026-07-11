#!/usr/bin/env python3

"""Single-window modern shell for HamRadio-Pi Ultimate."""

from __future__ import annotations

import platform
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import ttk

from services.config_service import ConfigService
from services.weather_service import (
    WeatherError,
    fetch_current_weather,
    format_weather_summary,
)
from ui import AppTheme, ToastManager, ToolTip


PROJECT_DIR = Path(__file__).resolve().parent.parent
STATION_FILE = PROJECT_DIR / "config" / "station.json"
SETTINGS_FILE = PROJECT_DIR / "config" / "settings.json"
APPLICATION_FILE = PROJECT_DIR / "src" / "data" / "applications.json"
VERSION_FILE = PROJECT_DIR / "config" / "version.json"

TOOLS = {
    "station": PROJECT_DIR / "src" / "station_wizard.py",
    "applications": PROJECT_DIR / "src" / "application_browser.py",
    "hardware": PROJECT_DIR / "src" / "hardware.py",
    "settings": PROJECT_DIR / "src" / "settings.py",
    "updates": PROJECT_DIR / "src" / "updater.py",
    "builder": PROJECT_DIR / "src" / "station_builder.py",
}

WPSD_SCRIPT = PROJECT_DIR / "scripts" / "wpsd-card-builder.sh"


class HamRadioPiShell:
    """Single main window with sidebar page navigation."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate")
        self.root.geometry("1280x800")
        self.root.minsize(1080, 680)

        AppTheme.apply(root)

        self.station = ConfigService.load_json(STATION_FILE, {})
        self.catalogue = ConfigService.load_json(
            APPLICATION_FILE,
            {"applications": []},
        )
        self.version = ConfigService.load_json(
            VERSION_FILE,
            {"version": "0.5.1", "edition": "Community"},
        )

        self.toast = ToastManager(root)
        self.tooltips: list[ToolTip] = []
        self.nav_buttons: dict[str, ttk.Button] = {}
        self.current_page = "dashboard"

        self.search_value = tk.StringVar()
        self.callsign_value = tk.StringVar()
        self.grid_value = tk.StringVar()
        self.utc_value = tk.StringVar()
        self.local_value = tk.StringVar()
        self.weather_value = tk.StringVar(value="Loading...")
        self.health_value = tk.StringVar(value="Ready")

        self.weather_job: str | None = None
        self.weather_loading = False

        self.build_shell()
        self.refresh_station()
        self.show_page("dashboard")
        self.update_clocks()
        self.refresh_weather()

    def build_shell(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame")
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)

        self.sidebar = ttk.Frame(
            shell,
            width=235,
            padding=(14, 18),
            style="Sidebar.TFrame",
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.content = ttk.Frame(
            shell,
            padding=24,
            style="App.TFrame",
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(1, weight=1)
        self.content.columnconfigure(0, weight=1)

        ttk.Label(
            self.sidebar,
            text="HamRadio-Pi",
            style="SidebarTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            self.sidebar,
            text="ULTIMATE",
            style="SidebarMuted.TLabel",
        ).pack(anchor="w", pady=(0, 18))

        nav_items = [
            ("dashboard", "⌂  Dashboard", "Station overview and quick controls."),
            ("station", "◉  Station", "Edit callsign, grid, radios and station profile."),
            ("applications", "▣  Applications", "Browse and install ham-radio applications."),
            ("wpsd", "▤  WPSD Builder", "Prepare WPSD SD cards and hotspot configuration."),
            ("hardware", "⌁  Hardware", "Detect radios, SDRs, CAT, audio and USB hardware."),
            ("health", "♥  Station Health", "Check system, hardware and software readiness."),
            ("propagation", "≈  Propagation", "View solar and propagation information."),
            ("weather", "☁  Weather", "View weather for your saved station location."),
            ("settings", "⚙  Settings", "Configure data sources and application preferences."),
            ("updates", "⇧  Updates", "Check and install HamRadio-Pi Ultimate updates."),
            ("help", "?  Help", "Open help, project information and useful links."),
        ]

        for key, text, tip in nav_items:
            button = ttk.Button(
                self.sidebar,
                text=text,
                command=lambda page=key: self.show_page(page),
                style="Sidebar.TButton",
            )
            button.pack(fill="x", pady=2)
            self.nav_buttons[key] = button
            self.tooltips.append(ToolTip(button, tip))

        spacer = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        spacer.pack(fill="both", expand=True)

        edition = self.version.get("edition", "Community")
        version = self.version.get("version", "0.5.1")

        ttk.Label(
            self.sidebar,
            text=f"{edition} Edition",
            style="SidebarMuted.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            self.sidebar,
            text=f"Version {version}",
            style="SidebarMuted.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        self.topbar = ttk.Frame(self.content, style="App.TFrame")
        self.topbar.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        self.topbar.columnconfigure(0, weight=1)

        self.page_title = ttk.Label(
            self.topbar,
            text="Dashboard",
            style="PageTitle.TLabel",
        )
        self.page_title.grid(row=0, column=0, sticky="w")

        search = ttk.Entry(
            self.topbar,
            textvariable=self.search_value,
            style="Modern.TEntry",
            width=32,
        )
        search.grid(row=0, column=1, sticky="e")
        search.insert(0, "Search HamRadio-Pi Ultimate")
        search.bind("<FocusIn>", self._clear_search_hint)
        search.bind("<Return>", self.run_search)
        self.tooltips.append(
            ToolTip(
                search,
                "Search applications, station tools, hardware, weather and settings.",
            )
        )

        self.page_host = ttk.Frame(self.content, style="App.TFrame")
        self.page_host.grid(row=1, column=0, sticky="nsew")
        self.page_host.columnconfigure(0, weight=1)
        self.page_host.rowconfigure(0, weight=1)

    def _clear_search_hint(self, _event=None) -> None:
        if self.search_value.get() == "Search HamRadio-Pi Ultimate":
            self.search_value.set("")

    def run_search(self, _event=None) -> None:
        query = self.search_value.get().strip().lower()
        if not query or query == "search hamradio-pi ultimate":
            return

        application_names = [
            str(item.get("name", ""))
            for item in self.catalogue.get("applications", [])
            if isinstance(item, dict)
        ]
        matches = [name for name in application_names if query in name.lower()]

        keywords = {
            "weather": "weather",
            "radio": "station",
            "callsign": "station",
            "grid": "station",
            "usb": "hardware",
            "sdr": "hardware",
            "cat": "hardware",
            "update": "updates",
            "wpsd": "wpsd",
            "mmdvm": "wpsd",
            "health": "health",
            "settings": "settings",
        }

        for key, page in keywords.items():
            if key in query:
                self.show_page(page)
                self.toast.show(f"Opened {page.title()} for “{query}”.", "info")
                return

        if matches:
            self.show_page("applications")
            self.toast.show(
                "Application matches: " + ", ".join(matches[:5]),
                "success",
            )
        else:
            self.toast.show(f'No result found for “{query}”.', "warning")

    def clear_page(self) -> None:
        for child in self.page_host.winfo_children():
            child.destroy()

    def show_page(self, page: str) -> None:
        self.current_page = page
        self.clear_page()

        titles = {
            "dashboard": "Dashboard",
            "station": "Station",
            "applications": "Applications",
            "wpsd": "WPSD Builder",
            "hardware": "Hardware",
            "health": "Station Health",
            "propagation": "Propagation",
            "weather": "Weather",
            "settings": "Settings",
            "updates": "Updates",
            "help": "Help",
        }
        self.page_title.configure(text=titles.get(page, page.title()))

        for key, button in self.nav_buttons.items():
            button.configure(
                style="SidebarActive.TButton" if key == page else "Sidebar.TButton"
            )

        builders = {
            "dashboard": self.build_dashboard_page,
            "station": self.build_station_page,
            "applications": self.build_applications_page,
            "wpsd": self.build_wpsd_page,
            "hardware": self.build_hardware_page,
            "health": self.build_health_page,
            "propagation": self.build_propagation_page,
            "weather": self.build_weather_page,
            "settings": self.build_settings_page,
            "updates": self.build_updates_page,
            "help": self.build_help_page,
        }

        builders.get(page, self.build_dashboard_page)()

    def page_frame(self) -> ttk.Frame:
        frame = ttk.Frame(self.page_host, style="App.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        return frame

    @staticmethod
    def card(parent: ttk.Frame, title: str) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=18, style="Card.TFrame")
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        return frame

    @staticmethod
    def card_row(parent: ttk.Frame, label: str, variable: tk.StringVar) -> None:
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, style="CardLabel.TLabel").pack(side="left")
        ttk.Label(
            row,
            textvariable=variable,
            style="CardValue.TLabel",
            wraplength=350,
            justify="right",
        ).pack(side="right")

    def action_button(
        self,
        parent: ttk.Frame,
        text: str,
        command,
        tooltip: str,
        accent: bool = False,
    ) -> ttk.Button:
        button = ttk.Button(
            parent,
            text=text,
            command=command,
            style="Accent.TButton" if accent else "Modern.TButton",
        )
        self.tooltips.append(ToolTip(button, tooltip))
        return button

    def build_dashboard_page(self) -> None:
        frame = self.page_frame()
        frame.columnconfigure((0, 1), weight=1, uniform="dash")
        frame.rowconfigure((0, 1), weight=1, uniform="dash")

        station = self.card(frame, "My Station")
        station.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.card_row(station, "Callsign", self.callsign_value)
        self.card_row(station, "Grid", self.grid_value)
        self.card_row(station, "UTC", self.utc_value)
        self.card_row(station, "Local Time", self.local_value)

        status = self.card(frame, "Station Status")
        status.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        self.card_row(status, "Health", self.health_value)
        radio = tk.StringVar(value=self.station.get("preferred_radio") or "Not configured")
        sdr = tk.StringVar(value=self.station.get("preferred_sdr") or "Not configured")
        self.card_row(status, "Radio", radio)
        self.card_row(status, "SDR", sdr)

        info = self.card(frame, "Live Information")
        info.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(8, 0))
        self.card_row(info, "Weather", self.weather_value)
        solar = tk.StringVar(value="Coming soon")
        propagation = tk.StringVar(value="Coming soon")
        self.card_row(info, "Solar", solar)
        self.card_row(info, "Propagation", propagation)

        quick = self.card(frame, "Quick Actions")
        quick.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(8, 0))

        quick_grid = ttk.Frame(
            quick,
            style="Card.TFrame",
        )
        quick_grid.pack(
            fill="both",
            expand=True,
        )

        for column in (0, 1):
            quick_grid.columnconfigure(
                column,
                weight=1,
            )

        buttons = [
            ("Applications", lambda: self.show_page("applications"), "Browse and install software."),
            ("Hardware", lambda: self.show_page("hardware"), "Detect radio and USB hardware."),
            ("WPSD Builder", lambda: self.show_page("wpsd"), "Prepare a WPSD hotspot SD card."),
            ("Settings", lambda: self.show_page("settings"), "Configure HamRadio-Pi Ultimate."),
        ]
        for index, (text, command, tip) in enumerate(buttons):
            button = self.action_button(
                quick_grid,
                text,
                command,
                tip,
            )
            button.grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=5,
                pady=5,
            )

    def build_station_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Station Profile")
        card.pack(fill="x")

        text = ttk.Label(
            card,
            text=(
                "Manage callsign, grid square, DMR ID, preferred radio, "
                "preferred SDR and station type."
            ),
            style="CardValue.TLabel",
            wraplength=760,
            justify="left",
        )
        text.pack(anchor="w", pady=(0, 16))

        button = self.action_button(
            card,
            "Open Station Profile Editor",
            lambda: self.open_tool("station", "Station Profile"),
            "Edit your complete station profile.",
            accent=True,
        )
        button.pack(anchor="w")

    def build_applications_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Applications")
        card.pack(fill="both", expand=True)

        apps = self.catalogue.get("applications", [])
        count = len(apps) if isinstance(apps, list) else 0

        ttk.Label(
            card,
            text=f"{count} catalogue applications are currently available.",
            style="CardValue.TLabel",
        ).pack(anchor="w", pady=(0, 14))

        names = tk.Listbox(
            card,
            background=AppTheme.SURFACE_ALT,
            foreground=AppTheme.TEXT,
            selectbackground=AppTheme.ACCENT,
            selectforeground=AppTheme.TEXT,
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
            height=14,
        )
        names.pack(fill="both", expand=True)

        for item in apps:
            if isinstance(item, dict):
                names.insert(
                    tk.END,
                    f"{item.get('name', 'Unknown')}  ·  {item.get('category', 'Other')}",
                )

        button = self.action_button(
            card,
            "Open Full Application Manager",
            lambda: self.open_tool("applications", "Applications"),
            "Open the detailed software browser and installer.",
            accent=True,
        )
        button.pack(anchor="e", pady=(14, 0))

    def build_wpsd_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "WPSD and MMDVM")
        card.pack(fill="x")

        ttk.Label(
            card,
            text=(
                "Prepare an SD card for a separate WPSD MMDVM hotspot. "
                "Offline Wi-Fi configuration will be integrated here next."
            ),
            style="CardValue.TLabel",
            wraplength=780,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        button = self.action_button(
            card,
            "Open WPSD SD Card Builder",
            self.open_wpsd,
            "Download and write a WPSD image for a separate hotspot Pi.",
            accent=True,
        )
        button.pack(anchor="w")

    def build_hardware_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Hardware Detection")
        card.pack(fill="x")

        ttk.Label(
            card,
            text=(
                "Detect USB devices, CAT interfaces, serial ports, sound cards, "
                "SDRs, GPS receivers and MMDVM modems."
            ),
            style="CardValue.TLabel",
            wraplength=780,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        button = self.action_button(
            card,
            "Run Hardware Detection",
            lambda: self.open_tool("hardware", "Hardware Detection"),
            "Scan this computer for connected ham-radio hardware.",
            accent=True,
        )
        button.pack(anchor="w")

    def build_health_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Station Health")
        card.pack(fill="x")

        checks = [
            "Python runtime: Ready",
            "Project files: Ready",
            "Station profile: " + ("Ready" if self.station.get("callsign") else "Needs attention"),
            "Weather configuration: " + (
                "Ready"
                if ConfigService.load_json(SETTINGS_FILE, {}).get("weather")
                else "Needs attention"
            ),
        ]

        for check in checks:
            ttk.Label(
                card,
                text="• " + check,
                style="CardValue.TLabel",
            ).pack(anchor="w", pady=4)

        button = self.action_button(
            card,
            "Run Full Health Check",
            self.run_health_check,
            "Check basic project, station and weather readiness.",
            accent=True,
        )
        button.pack(anchor="w", pady=(16, 0))

    def build_propagation_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Propagation")
        card.pack(fill="x")
        ttk.Label(
            card,
            text=(
                "Solar conditions, HF propagation and band guidance will be "
                "displayed here in a future update."
            ),
            style="CardValue.TLabel",
            wraplength=760,
            justify="left",
        ).pack(anchor="w")

    def build_weather_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Current Weather")
        card.pack(fill="x")

        ttk.Label(
            card,
            textvariable=self.weather_value,
            style="CardValue.TLabel",
            font=("Segoe UI", 16, "bold"),
            wraplength=760,
        ).pack(anchor="w", pady=(0, 16))

        button = self.action_button(
            card,
            "Refresh Weather",
            self.refresh_weather,
            "Download the latest weather for your saved location.",
            accent=True,
        )
        button.pack(anchor="w")

    def build_settings_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Settings")
        card.pack(fill="x")

        ttk.Label(
            card,
            text=(
                "Configure weather sources, location, API keys and future "
                "application preferences."
            ),
            style="CardValue.TLabel",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        button = self.action_button(
            card,
            "Open Settings",
            lambda: self.open_tool("settings", "Settings"),
            "Open the full settings editor.",
            accent=True,
        )
        button.pack(anchor="w")

    def build_updates_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Updates")
        card.pack(fill="x")

        ttk.Label(
            card,
            text=(
                "Check GitHub for a newer version, back up local settings and "
                "install updates safely."
            ),
            style="CardValue.TLabel",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        button = self.action_button(
            card,
            "Open Update Manager",
            lambda: self.open_tool("updates", "Update Manager"),
            "Check for and install HamRadio-Pi Ultimate updates.",
            accent=True,
        )
        button.pack(anchor="w")

    def build_help_page(self) -> None:
        frame = self.page_frame()
        card = self.card(frame, "Help and About")
        card.pack(fill="x")

        version = self.version.get("version", "0.5.1")
        edition = self.version.get("edition", "Community")

        ttk.Label(
            card,
            text=(
                f"HamRadio-Pi Ultimate {edition} Edition\n"
                f"Version {version}\n\n"
                "One command. One wizard. One Ham Radio menu."
            ),
            style="CardValue.TLabel",
            justify="left",
        ).pack(anchor="w")

    def refresh_station(self) -> None:
        self.station = ConfigService.load_json(STATION_FILE, {})
        self.callsign_value.set(self.station.get("callsign") or "Not configured")
        self.grid_value.set(self.station.get("grid_square") or "Not configured")

    def update_clocks(self) -> None:
        self.utc_value.set(datetime.now(timezone.utc).strftime("%H:%M:%S UTC"))
        self.local_value.set(datetime.now().astimezone().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clocks)

    def refresh_weather(self) -> None:
        if self.weather_loading:
            return

        if self.weather_job is not None:
            self.root.after_cancel(self.weather_job)
            self.weather_job = None

        self.weather_loading = True
        self.weather_value.set("Updating weather...")

        threading.Thread(
            target=self._weather_worker,
            daemon=True,
        ).start()

    def _weather_worker(self) -> None:
        settings = ConfigService.load_json(SETTINGS_FILE, {})
        station = ConfigService.load_json(STATION_FILE, {})

        try:
            weather = fetch_current_weather(settings, station)
            summary = format_weather_summary(weather)
            level = "success"
        except WeatherError as error:
            summary = str(error)
            level = "warning"

        self.root.after(
            0,
            lambda: self._finish_weather(summary, settings, level),
        )

    def _finish_weather(
        self,
        summary: str,
        settings: dict,
        level: str,
    ) -> None:
        self.weather_value.set(summary)
        self.weather_loading = False

        if self.current_page == "weather":
            self.show_page("weather")

        self.toast.show(summary, level)

        weather_settings = settings.get("weather", {})
        minutes = 20
        if isinstance(weather_settings, dict):
            try:
                minutes = int(weather_settings.get("refresh_minutes", 20))
            except (TypeError, ValueError):
                minutes = 20

        minutes = max(5, min(minutes, 120))
        self.weather_job = self.root.after(
            minutes * 60 * 1000,
            self.refresh_weather,
        )

    def open_tool(self, key: str, title: str) -> None:
        path = TOOLS[key]
        if not path.exists():
            self.toast.show(f"{title} could not be found.", "error")
            return

        try:
            subprocess.run([sys.executable, str(path)], check=False)
        except OSError as error:
            self.toast.show(f"{title} could not start: {error}", "error")
            return

        self.refresh_station()
        self.toast.show(f"{title} closed.", "info")

    def open_wpsd(self) -> None:
        if platform.system() != "Linux":
            self.toast.show(
                "The WPSD SD Card Builder runs on Raspberry Pi OS.",
                "warning",
            )
            return

        if not WPSD_SCRIPT.exists():
            self.toast.show("WPSD builder script not found.", "error")
            return

        try:
            subprocess.Popen(["bash", str(WPSD_SCRIPT)])
            self.toast.show("WPSD SD Card Builder opened.", "success")
        except OSError as error:
            self.toast.show(f"WPSD builder failed: {error}", "error")

    def run_health_check(self) -> None:
        problems = 0

        if not self.station.get("callsign"):
            problems += 1

        settings = ConfigService.load_json(SETTINGS_FILE, {})
        if not settings.get("weather"):
            problems += 1

        if problems:
            self.health_value.set(f"Attention needed ({problems})")
            self.toast.show(
                f"Station Health found {problems} item(s) needing attention.",
                "warning",
            )
        else:
            self.health_value.set("Healthy")
            self.toast.show("Station Health check passed.", "success")

        self.show_page("health")


def main() -> None:
    root = tk.Tk()
    HamRadioPiShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()
