from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from constants import COLORS


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None) -> None:
        self.widget.after(450, self._show)

    def _show(self) -> None:
        if self.tip is not None or not self.widget.winfo_exists():
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        x = self.widget.winfo_rootx() + 16
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=self.text,
            bg="#07111D",
            fg=COLORS["text"],
            padx=10,
            pady=7,
            relief="solid",
            borderwidth=1,
            wraplength=360,
            justify="left",
            font=("DejaVu Sans", 9),
        ).pack()

    def _hide(self, _event=None) -> None:
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


def action_button(
    parent: tk.Widget,
    text: str,
    command: Callable,
    small: bool = False,
    secondary: bool = False,
) -> tk.Button:
    bg = COLORS["panel_alt"] if secondary else COLORS["teal_dark"]
    active = COLORS["border"] if secondary else COLORS["teal_hover"]
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg="white",
        activebackground=active,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        padx=10 if small else 14,
        pady=6 if small else 9,
        cursor="hand2",
        font=("DejaVu Sans", 8 if small else 9, "bold"),
    )


class Card(tk.Frame):
    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(
            parent,
            bg=COLORS["panel"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            bd=0,
            **kwargs,
        )


class MetricCard(Card):
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        icon: str,
        value: str = "—",
        detail: str = "",
    ) -> None:
        super().__init__(parent)

        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill="x", padx=15, pady=(13, 4))

        self.icon_label = tk.Label(
            top,
            text=icon,
            bg=COLORS["panel_alt"],
            fg=COLORS["teal"],
            width=3,
            height=1,
            font=("DejaVu Sans", 12, "bold"),
        )
        self.icon_label.pack(side="left")

        self.title_label = tk.Label(
            top,
            text=title,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("DejaVu Sans", 9, "bold"),
        )
        self.title_label.pack(side="left", padx=(10, 0))

        self.value_label = tk.Label(
            self,
            text=value,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("DejaVu Sans", 18, "bold"),
        )
        self.value_label.pack(anchor="w", padx=15)

        self.detail_label = tk.Label(
            self,
            text=detail,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("DejaVu Sans", 8),
            wraplength=220,
            justify="left",
        )
        self.detail_label.pack(anchor="w", padx=15, pady=(5, 13))

    def set(self, value: str, detail: str = "", colour: Optional[str] = None) -> None:
        self.value_label.configure(text=value, fg=colour or COLORS["text"])
        self.detail_label.configure(text=detail)


class SectionTitle(tk.Frame):
    def __init__(self, parent: tk.Widget, title: str, subtitle: str = "") -> None:
        super().__init__(parent, bg=COLORS["background"])
        tk.Label(
            self,
            text=title,
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("DejaVu Sans", 13, "bold"),
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                self,
                text=subtitle,
                bg=COLORS["background"],
                fg=COLORS["muted"],
                font=("DejaVu Sans", 9),
            ).pack(anchor="w", pady=(2, 0))
