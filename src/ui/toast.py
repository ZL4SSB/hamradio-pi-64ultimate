"""Inline toast notifications."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .theme import AppTheme


class ToastManager:
    def __init__(self, root: tk.Misc) -> None:
        self.root = root
        self.window: tk.Toplevel | None = None

    def show(
        self,
        message: str,
        level: str = "info",
        duration_ms: int = 3200,
    ) -> None:
        if self.window is not None:
            self.window.destroy()

        colours = {
            "success": AppTheme.GOOD,
            "warning": AppTheme.WARNING,
            "error": AppTheme.ERROR,
            "info": AppTheme.ACCENT,
        }
        accent = colours.get(level, AppTheme.ACCENT)

        window = tk.Toplevel(self.root)
        window.overrideredirect(True)
        window.attributes("-topmost", True)

        frame = tk.Frame(
            window,
            background=AppTheme.SURFACE,
            highlightbackground=accent,
            highlightthickness=2,
        )
        frame.pack()

        label = tk.Label(
            frame,
            text=message,
            background=AppTheme.SURFACE,
            foreground=AppTheme.TEXT,
            padx=18,
            pady=12,
            font=("Segoe UI", 10, "bold"),
            wraplength=420,
            justify="left",
        )
        label.pack()

        self.root.update_idletasks()
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        x = self.root.winfo_rootx() + self.root.winfo_width() - width - 28
        y = self.root.winfo_rooty() + self.root.winfo_height() - height - 28
        window.geometry(f"+{x}+{y}")

        self.window = window
        window.after(duration_ms, self._close)

    def _close(self) -> None:
        if self.window is not None:
            self.window.destroy()
            self.window = None
