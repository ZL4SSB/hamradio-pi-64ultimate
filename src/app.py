#!/usr/bin/env python3

import tkinter as tk
from dashboard import HamRadioPiUltimate


def main() -> None:
    root = tk.Tk()
    HamRadioPiUltimate(root)
    root.mainloop()


if __name__ == "__main__":
    main()
