#!/usr/bin/env python3

"""Hardware detection window for HamRadio-Pi Ultimate."""

from __future__ import annotations

import glob
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk


class HardwareWindow:
    """Display hardware information useful to amateur-radio operators."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Hardware")
        self.root.geometry("920x680")
        self.root.minsize(760, 560)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

        self.summary_value = tk.StringVar(
            value="Press Refresh Hardware to scan this computer."
        )

        self.build_interface()
        self.refresh_hardware()

    def build_interface(self) -> None:
        """Create the hardware-detection interface."""

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
            text="Hardware Detection",
            font=("Arial", 15),
        ).pack(pady=(6, 4))

        ttk.Label(
            main,
            textvariable=self.summary_value,
            wraplength=840,
            justify="left",
        ).pack(fill="x", pady=(0, 12))

        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)

        self.overview_box = self.add_text_tab(
            notebook,
            "Overview",
        )
        self.usb_box = self.add_text_tab(
            notebook,
            "USB Devices",
        )
        self.serial_box = self.add_text_tab(
            notebook,
            "Serial Ports",
        )
        self.audio_box = self.add_text_tab(
            notebook,
            "Audio Devices",
        )
        self.radio_box = self.add_text_tab(
            notebook,
            "Radio / SDR Hints",
        )

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(12, 0))

        ttk.Button(
            buttons,
            text="Refresh Hardware",
            command=self.refresh_hardware,
        ).pack(side="left")

        ttk.Button(
            buttons,
            text="Close",
            command=self.root.destroy,
        ).pack(side="right")

    @staticmethod
    def add_text_tab(
        notebook: ttk.Notebook,
        title: str,
    ) -> scrolledtext.ScrolledText:
        """Add a read-only text tab."""

        frame = ttk.Frame(
            notebook,
            padding=10,
        )
        notebook.add(
            frame,
            text=title,
        )

        text_box = scrolledtext.ScrolledText(
            frame,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
        )
        text_box.pack(
            fill="both",
            expand=True,
        )

        return text_box

    @staticmethod
    def set_text(
        text_box: scrolledtext.ScrolledText,
        content: str,
    ) -> None:
        """Replace the contents of a read-only text widget."""

        text_box.configure(
            state="normal",
        )
        text_box.delete(
            "1.0",
            tk.END,
        )
        text_box.insert(
            tk.END,
            content.strip() + "\n",
        )
        text_box.configure(
            state="disabled",
        )

    @staticmethod
    def run_command(
        command: list[str],
    ) -> str:
        """Run a local hardware command safely."""

        try:
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
                timeout=12,
            )
        except (
            OSError,
            subprocess.TimeoutExpired,
        ):
            return ""

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    def refresh_hardware(self) -> None:
        """Scan the current computer and update all tabs."""

        system_name = platform.system()

        overview = self.build_overview(system_name)
        usb = self.detect_usb(system_name)
        serial = self.detect_serial(system_name)
        audio = self.detect_audio(system_name)
        radio = self.detect_radio_hints(
            usb,
            serial,
            audio,
        )

        self.set_text(
            self.overview_box,
            overview,
        )
        self.set_text(
            self.usb_box,
            usb,
        )
        self.set_text(
            self.serial_box,
            serial,
        )
        self.set_text(
            self.audio_box,
            audio,
        )
        self.set_text(
            self.radio_box,
            radio,
        )

        counts = [
            item
            for item in [
                "USB devices scanned",
                "serial ports scanned",
                "audio devices scanned",
            ]
        ]

        self.summary_value.set(
            "Hardware scan complete. "
            + ", ".join(counts)
            + "."
        )

    def build_overview(
        self,
        system_name: str,
    ) -> str:
        """Build general computer information."""

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
            model_path = Path(
                "/proc/device-tree/model"
            )

            if model_path.exists():
                try:
                    model = model_path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    ).replace(
                        "\x00",
                        "",
                    ).strip()
                except OSError:
                    model = ""

                if model:
                    lines.extend(
                        [
                            "",
                            f"Raspberry Pi model: {model}",
                        ]
                    )

            kernel = self.run_command(
                [
                    "uname",
                    "-a",
                ]
            )

            if kernel:
                lines.extend(
                    [
                        "",
                        "Kernel:",
                        kernel,
                    ]
                )

        return "\n".join(lines)

    def detect_usb(
        self,
        system_name: str,
    ) -> str:
        """Detect connected USB devices."""

        if system_name == "Linux":
            output = self.run_command(
                [
                    "lsusb",
                ]
            )

            return (
                output
                or (
                    "No USB information was returned.\n\n"
                    "Install usbutils on Raspberry Pi OS:\n"
                    "sudo apt install usbutils"
                )
            )

        if system_name == "Windows":
            output = self.run_command(
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
            )

            return (
                output
                or "No USB information was returned by Windows."
            )

        return (
            "USB detection is not yet implemented "
            "for this operating system."
        )

    def detect_serial(
        self,
        system_name: str,
    ) -> str:
        """Detect likely CAT, GPS, and programming serial ports."""

        if system_name == "Linux":
            devices = []

            for pattern in [
                "/dev/ttyUSB*",
                "/dev/ttyACM*",
                "/dev/serial/by-id/*",
                "/dev/ttyAMA*",
            ]:
                devices.extend(
                    glob.glob(pattern)
                )

            if not devices:
                return (
                    "No common serial devices were detected.\n\n"
                    "Expected examples:\n"
                    "/dev/ttyUSB0\n"
                    "/dev/ttyACM0\n"
                    "/dev/serial/by-id/..."
                )

            return "\n".join(
                sorted(
                    set(devices)
                )
            )

        if system_name == "Windows":
            output = self.run_command(
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
            )

            return (
                output
                or "No Windows COM ports were detected."
            )

        return (
            "Serial-port detection is not yet implemented "
            "for this operating system."
        )

    def detect_audio(
        self,
        system_name: str,
    ) -> str:
        """Detect audio devices commonly used for digital modes."""

        if system_name == "Linux":
            output = self.run_command(
                [
                    "aplay",
                    "-l",
                ]
            )

            if not output:
                output = self.run_command(
                    [
                        "pactl",
                        "list",
                        "short",
                        "sinks",
                    ]
                )

            return (
                output
                or (
                    "No audio information was returned.\n\n"
                    "Install ALSA utilities if needed:\n"
                    "sudo apt install alsa-utils"
                )
            )

        if system_name == "Windows":
            output = self.run_command(
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
            )

            return (
                output
                or "No Windows sound devices were detected."
            )

        return (
            "Audio-device detection is not yet implemented "
            "for this operating system."
        )

    @staticmethod
    def detect_radio_hints(
        usb_text: str,
        serial_text: str,
        audio_text: str,
    ) -> str:
        """Look for common ham-radio hardware keywords."""

        combined = (
            usb_text
            + "\n"
            + serial_text
            + "\n"
            + audio_text
        ).lower()

        hints: list[str] = []

        keyword_groups = {
            "Possible RTL-SDR device": [
                "rtl",
                "realtek",
                "2838",
                "2832",
            ],
            "Possible SDRplay device": [
                "sdrplay",
                "rsp1",
                "rspdx",
            ],
            "Possible Airspy device": [
                "airspy",
            ],
            "Possible HackRF device": [
                "hackrf",
            ],
            "Possible Icom USB device": [
                "icom",
                "silicon labs cp210",
            ],
            "Possible Yaesu USB device": [
                "yaesu",
            ],
            "Possible Kenwood USB device": [
                "kenwood",
            ],
            "Possible Xiegu / USB serial device": [
                "xiegu",
                "cp210",
                "ch340",
                "ftdi",
            ],
            "Possible Digirig interface": [
                "digirig",
            ],
            "Possible USB sound interface": [
                "usb audio",
                "audio codec",
                "cm108",
                "cm119",
            ],
            "Possible GPS receiver": [
                "gps",
                "ublox",
                "u-blox",
            ],
            "Possible MMDVM modem": [
                "mmdvm",
                "zumspot",
                "stm32",
            ],
        }

        for label, keywords in keyword_groups.items():
            if any(
                keyword in combined
                for keyword in keywords
            ):
                hints.append(
                    f"• {label}"
                )

        if not hints:
            return (
                "No obvious ham-radio hardware keywords were found.\n\n"
                "This does not mean hardware is absent. Some devices "
                "appear only as generic USB serial or audio interfaces."
            )

        return (
            "POSSIBLE HAM-RADIO HARDWARE\n"
            "===========================\n\n"
            + "\n".join(hints)
            + "\n\n"
            "These are identification hints only. "
            "Exact device confirmation will be added later."
        )


def main() -> None:
    root = tk.Tk()
    HardwareWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
