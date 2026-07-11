#!/usr/bin/env python3

"""HamRadio-Pi Ultimate application entry point."""

import tkinter as tk

from dashboard import HamRadioPiUltimate


def main() -> None:
    """Start HamRadio-Pi Ultimate."""

    root = tk.Tk()
    HamRadioPiUltimate(root)
    root.mainloop()


if __name__ == "__main__":
    main()
