"""Shared modern styling for HamRadio-Pi Ultimate."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

class AppTheme:
    BG = "#121820"
    SURFACE = "#1b2430"
    SURFACE_ALT = "#222d3a"
    BORDER = "#334155"
    TEXT = "#f1f5f9"
    MUTED = "#94a3b8"
    ACCENT = "#22c55e"
    ACCENT_HOVER = "#16a34a"
    BUTTON = "#2b3948"
    BUTTON_HOVER = "#3a4a5c"

    @classmethod
    def apply(cls, root: tk.Misc) -> ttk.Style:
        root.configure(bg=cls.BG)
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=cls.BG, foreground=cls.TEXT, font=("Segoe UI", 10))
        style.configure("App.TFrame", background=cls.BG)
        style.configure("Card.TFrame", background=cls.SURFACE)
        style.configure("Header.TLabel", background=cls.BG, foreground=cls.TEXT, font=("Segoe UI", 25, "bold"))
        style.configure("Subheader.TLabel", background=cls.BG, foreground=cls.MUTED, font=("Segoe UI", 11))
        style.configure("CardTitle.TLabel", background=cls.SURFACE, foreground=cls.TEXT, font=("Segoe UI", 12, "bold"))
        style.configure("CardLabel.TLabel", background=cls.SURFACE, foreground=cls.MUTED, font=("Segoe UI", 10))
        style.configure("CardValue.TLabel", background=cls.SURFACE, foreground=cls.TEXT, font=("Segoe UI", 10, "bold"))
        style.configure("StatusGood.TLabel", background=cls.SURFACE, foreground=cls.ACCENT, font=("Segoe UI", 10, "bold"))
        style.configure("Footer.TLabel", background=cls.BG, foreground=cls.MUTED, font=("Segoe UI", 9))
        style.configure("Modern.TButton", background=cls.BUTTON, foreground=cls.TEXT, borderwidth=0, padding=(16,11), font=("Segoe UI",10,"bold"))
        style.map("Modern.TButton", background=[("active", cls.BUTTON_HOVER), ("pressed", cls.SURFACE_ALT)])
        style.configure("Accent.TButton", background=cls.ACCENT, foreground="#07120a", borderwidth=0, padding=(16,11), font=("Segoe UI",10,"bold"))
        style.map("Accent.TButton", background=[("active", cls.ACCENT_HOVER), ("pressed", cls.ACCENT_HOVER)])
        return style
