#!/usr/bin/env python3
import tkinter as tk
from main_window import MainWindow
from ui.splash_screen import SplashScreen

def main() -> int:
    root = tk.Tk()
    root.withdraw()
    splash = SplashScreen(root)
    splash.set_progress(15, "Loading interface…")
    root.after(350, lambda: splash.set_progress(45, "Loading services…"))
    root.after(700, lambda: splash.set_progress(75, "Preparing dashboard…"))

    def launch():
        splash.set_progress(100, "Ready")
        splash.destroy()
        root.destroy()
        app = MainWindow()
        app.mainloop()

    root.after(1100, launch)
    root.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
