#!/usr/bin/env python3

"""Modern hardware detection window."""

from __future__ import annotations

import glob
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext, ttk

from ui import AppTheme, ToolTip


class HardwareWindow:
    """Display hardware useful to amateur-radio operators."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Hardware")
        self.root.geometry("980x700")
        self.root.minsize(800, 580)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

        AppTheme.apply(self.root)

        self.summary_value = tk.StringVar(value="Scanning hardware...")
        self.tooltips: list[ToolTip] = []

        self.build_interface()
        self.refresh_hardware()

    def build_interface(self) -> None:
        main = ttk.Frame(self.root, padding=22, style="App.TFrame")
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main, style="App.TFrame")
        header.pack(fill="x", pady=(0, 16))

        title = ttk.Frame(header, style="App.TFrame")
        title.pack(side="left")

        ttk.Label(
            title,
            text="Hardware",
            style="Header.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            title,
            text="Detect radios, SDRs, serial ports, audio, GPS, and USB devices.",
            style="Subheader.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        close_button = ttk.Button(
            header,
            text="Close",
            command=self.root.destroy,
            style="Modern.TButton",
        )
        close_button.pack(side="right")
        self.tooltips.append(ToolTip(close_button, "Close the Hardware window."))

        summary_card = ttk.Frame(main, padding=16, style="Card.TFrame")
        summary_card.pack(fill="x", pady=(0, 14))

        ttk.Label(
            summary_card,
            textvariable=self.summary_value,
            style="CardValue.TLabel",
            wraplength=860,
            justify="left",
        ).pack(anchor="w")

        notebook = ttk.Notebook(main, style="Modern.TNotebook")
        notebook.pack(fill="both", expand=True)

        self.overview_box = self.add_text_tab(notebook, "Overview")
        self.usb_box = self.add_text_tab(notebook, "USB Devices")
        self.serial_box = self.add_text_tab(notebook, "Serial Ports")
        self.audio_box = self.add_text_tab(notebook, "Audio Devices")
        self.radio_box = self.add_text_tab(notebook, "Radio / SDR Hints")

        buttons = ttk.Frame(main, style="App.TFrame")
        buttons.pack(fill="x", pady=(14, 0))

        refresh = ttk.Button(
            buttons,
            text="Refresh Hardware",
            command=self.refresh_hardware,
            style="Accent.TButton",
        )
        refresh.pack(side="left")
        self.tooltips.append(
            ToolTip(
                refresh,
                "Scan the computer again for newly connected hardware.",
            )
        )

        ttk.Label(
            buttons,
            text="Press Esc to close",
            style="Footer.TLabel",
        ).pack(side="right")

    @staticmethod
    def add_text_tab(
        notebook: ttk.Notebook,
        title: str,
    ) -> scrolledtext.ScrolledText:
        frame = ttk.Frame(notebook, padding=10, style="App.TFrame")
        notebook.add(frame, text=title)

        box = scrolledtext.ScrolledText(
            frame,
            wrap="word",
            state="disabled",
            background=AppTheme.SURFACE,
            foreground=AppTheme.TEXT,
            insertbackground=AppTheme.TEXT,
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 10),
        )
        box.pack(fill="both", expand=True)
        return box

    @staticmethod
    def set_text(box: scrolledtext.ScrolledText, content: str) -> None:
        box.configure(state="normal")
        box.delete("1.0", tk.END)
        box.insert(tk.END, content.strip() + "\n")
        box.configure(state="disabled")

    @staticmethod
    def run_command(command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
                timeout=12,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""

        return result.stdout.strip() if result.returncode == 0 else ""

    def refresh_hardware(self) -> None:
        system_name = platform.system()

        overview = self.build_overview(system_name)
        usb = self.detect_usb(system_name)
        serial = self.detect_serial(system_name)
        audio = self.detect_audio(system_name)
        radio = self.detect_radio_hints(usb, serial, audio)

        self.set_text(self.overview_box, overview)
        self.set_text(self.usb_box, usb)
        self.set_text(self.serial_box, serial)
        self.set_text(self.audio_box, audio)
        self.set_text(self.radio_box, radio)

        self.summary_value.set(
            "Hardware scan complete. Open each tab to inspect the results."
        )

    def build_overview(self, system_name: str) -> str:
        lines = [
            "SYSTEM OVERVIEW",
            "===============",
            "",
            f"Operating system: {platform.platform()}",
            f"System type: {system_name}",
            f"Machine architecture: {platform.machine()}",
            f"Processor: {platform.processor() or 'Not reported'}",
            f"Python version: {platform.python_version()}",
        ]

        if system_name == "Linux":
            model_path = Path("/proc/device-tree/model")
            if model_path.exists():
                try:
                    model = model_path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    ).replace("\x00", "").strip()
                except OSError:
                    model = ""

                if model:
                    lines.extend(["", f"Raspberry Pi model: {model}"])

        return "\n".join(lines)

    def detect_usb(self, system_name: str) -> str:
        if system_name == "Linux":
            return self.run_command(["lsusb"]) or (
                "No USB information returned.\n\n"
                "Install usbutils with:\nsudo apt install usbutils"
            )

        if system_name == "Windows":
            return self.run_command(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Get-PnpDevice -PresentOnly | "
                        "Where-Object {$_.InstanceId -like 'USB*'} | "
                        "Select-Object Status,Class,FriendlyName | "
                        "Format-Table -AutoSize | Out-String"
                    ),
                ]
            ) or "No Windows USB information was returned."

        return "USB detection is not yet implemented for this operating system."

    def detect_serial(self, system_name: str) -> str:
        if system_name == "Linux":
            devices = []
            for pattern in [
                "/dev/ttyUSB*",
                "/dev/ttyACM*",
                "/dev/serial/by-id/*",
                "/dev/ttyAMA*",
            ]:
                devices.extend(glob.glob(pattern))

            return "\n".join(sorted(set(devices))) or (
                "No common serial devices were detected."
            )

        if system_name == "Windows":
            return self.run_command(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Get-CimInstance Win32_SerialPort | "
                        "Select-Object DeviceID,Name,Description | "
                        "Format-Table -AutoSize | Out-String"
                    ),
                ]
            ) or "No Windows COM ports were detected."

        return "Serial detection is not yet implemented for this operating system."

    def detect_audio(self, system_name: str) -> str:
        if system_name == "Linux":
            return (
                self.run_command(["aplay", "-l"])
                or self.run_command(["pactl", "list", "short", "sinks"])
                or "No audio information was returned."
            )

        if system_name == "Windows":
            return self.run_command(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Get-CimInstance Win32_SoundDevice | "
                        "Select-Object Status,Name,Manufacturer | "
                        "Format-Table -AutoSize | Out-String"
                    ),
                ]
            ) or "No Windows sound devices were detected."

        return "Audio detection is not yet implemented for this operating system."

    @staticmethod
    def detect_radio_hints(
        usb_text: str,
        serial_text: str,
        audio_text: str,
    ) -> str:
        combined = f"{usb_text}\n{serial_text}\n{audio_text}".lower()
        hints: list[str] = []

        groups = {
            "Possible RTL-SDR device": ["rtl", "realtek", "2838", "2832"],
            "Possible SDRplay device": ["sdrplay", "rsp1", "rspdx"],
            "Possible Airspy device": ["airspy"],
            "Possible HackRF device": ["hackrf"],
            "Possible radio or CAT interface": [
                "icom",
                "yaesu",
                "kenwood",
                "xiegu",
                "cp210",
                "ch340",
                "ftdi",
            ],
            "Possible Digirig interface": ["digirig"],
            "Possible USB sound interface": [
                "usb audio",
                "audio codec",
                "cm108",
                "cm119",
            ],
            "Possible GPS receiver": ["gps", "ublox", "u-blox"],
            "Possible MMDVM modem": ["mmdvm", "zumspot", "stm32"],
        }

        for label, keywords in groups.items():
            if any(keyword in combined for keyword in keywords):
                hints.append(f"• {label}")

        if not hints:
            return (
                "No obvious ham-radio hardware keywords were found.\n\n"
                "Some devices appear only as generic USB serial or audio interfaces."
            )

        return (
            "POSSIBLE HAM-RADIO HARDWARE\n"
            "===========================\n\n"
            + "\n".join(hints)
        )


def main() -> None:
    root = tk.Tk()
    HardwareWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
