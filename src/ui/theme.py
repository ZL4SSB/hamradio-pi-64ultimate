"""Modern shared theme for HamRadio-Pi Ultimate."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class AppTheme:
    BG = "#10161d"
    SIDEBAR = "#131c24"
    SURFACE = "#1a2530"
    SURFACE_ALT = "#22313d"
    BORDER = "#344654"

    TEXT = "#ffffff"
    TEXT_SOFT = "#e6edf3"
    MUTED = "#b8c7d1"

    ACCENT = "#0f766e"
    ACCENT_HOVER = "#0d9488"
    ACCENT_PRESSED = "#115e59"

    GOOD = "#22c55e"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    INFO = "#3b82f6"

    @classmethod
    def apply(cls, root: tk.Misc) -> ttk.Style:
        root.configure(bg=cls.BG)

        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            ".",
            background=cls.BG,
            foreground=cls.TEXT,
            font=("Segoe UI", 10),
        )

        style.configure("App.TFrame", background=cls.BG)
        style.configure("Sidebar.TFrame", background=cls.SIDEBAR)
        style.configure("Card.TFrame", background=cls.SURFACE)
        style.configure("CardAlt.TFrame", background=cls.SURFACE_ALT)

        style.configure(
            "Header.TLabel",
            background=cls.BG,
            foreground=cls.TEXT,
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "PageTitle.TLabel",
            background=cls.BG,
            foreground=cls.TEXT,
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "Subheader.TLabel",
            background=cls.BG,
            foreground=cls.TEXT_SOFT,
            font=("Segoe UI", 10),
        )
        style.configure(
            "SidebarTitle.TLabel",
            background=cls.SIDEBAR,
            foreground=cls.TEXT,
            font=("Segoe UI", 15, "bold"),
        )
        style.configure(
            "SidebarMuted.TLabel",
            background=cls.SIDEBAR,
            foreground=cls.MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "CardTitle.TLabel",
            background=cls.SURFACE,
            foreground=cls.TEXT,
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "CardLabel.TLabel",
            background=cls.SURFACE,
            foreground=cls.MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "CardValue.TLabel",
            background=cls.SURFACE,
            foreground=cls.TEXT,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Footer.TLabel",
            background=cls.BG,
            foreground=cls.MUTED,
            font=("Segoe UI", 9),
        )

        style.configure(
            "Sidebar.TButton",
            background=cls.SIDEBAR,
            foreground=cls.TEXT_SOFT,
            borderwidth=0,
            focusthickness=0,
            focuscolor=cls.SIDEBAR,
            anchor="w",
            padding=(14, 11),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Sidebar.TButton",
            background=[
                ("active", cls.SURFACE_ALT),
                ("pressed", cls.ACCENT_PRESSED),
            ],
            foreground=[("active", cls.TEXT)],
        )

        style.configure(
            "SidebarActive.TButton",
            background=cls.ACCENT,
            foreground=cls.TEXT,
            borderwidth=0,
            focusthickness=0,
            focuscolor=cls.ACCENT,
            anchor="w",
            padding=(14, 11),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "SidebarActive.TButton",
            background=[
                ("active", cls.ACCENT_HOVER),
                ("pressed", cls.ACCENT_PRESSED),
            ],
            foreground=[("active", cls.TEXT)],
        )

        style.configure(
            "Modern.TButton",
            background=cls.SURFACE_ALT,
            foreground=cls.TEXT,
            borderwidth=0,
            focusthickness=0,
            focuscolor=cls.SURFACE_ALT,
            padding=(15, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Modern.TButton",
            background=[
                ("active", cls.BORDER),
                ("pressed", cls.SURFACE),
            ],
            foreground=[("disabled", cls.MUTED)],
        )

        style.configure(
            "Accent.TButton",
            background=cls.ACCENT,
            foreground=cls.TEXT,
            borderwidth=0,
            focusthickness=0,
            focuscolor=cls.ACCENT,
            padding=(15, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", cls.ACCENT_HOVER),
                ("pressed", cls.ACCENT_PRESSED),
            ],
            foreground=[("active", cls.TEXT)],
        )

        style.configure(
            "Modern.TEntry",
            fieldbackground=cls.SURFACE_ALT,
            foreground=cls.TEXT,
            insertcolor=cls.TEXT,
            bordercolor=cls.BORDER,
            lightcolor=cls.BORDER,
            darkcolor=cls.BORDER,
            padding=9,
        )

        style.configure(
            "Modern.TCombobox",
            fieldbackground=cls.SURFACE_ALT,
            background=cls.SURFACE_ALT,
            foreground=cls.TEXT,
            arrowcolor=cls.TEXT,
            bordercolor=cls.BORDER,
            padding=7,
        )

        return style
