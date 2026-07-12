"""Hover tooltip helper."""

from __future__ import annotations

import tkinter as tk


class ToolTip:
    def __init__(
        self,
        widget: tk.Widget,
        text: str,
        delay_ms: int = 450,
        wraplength: int = 330,
    ) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.wraplength = wraplength
        self._job: str | None = None
        self._window: tk.Toplevel | None = None

        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None) -> None:
        self._cancel()
        self._job = self.widget.after(self.delay_ms, self._show)

    def _cancel(self) -> None:
        if self._job is not None:
            self.widget.after_cancel(self._job)
            self._job = None

    def _show(self) -> None:
        if self._window is not None or not self.text:
            return

        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8

        window = tk.Toplevel(self.widget)
        window.wm_overrideredirect(True)
        window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            window,
            text=self.text,
            justify="left",
            wraplength=self.wraplength,
            background="#0b1117",
            foreground="#ffffff",
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=8,
            font=("Segoe UI", 9),
        )
        label.pack()
        self._window = window

    def _hide(self, _event=None) -> None:
        self._cancel()
        if self._window is not None:
            self._window.destroy()
            self._window = None
