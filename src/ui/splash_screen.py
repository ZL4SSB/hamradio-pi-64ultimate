from __future__ import annotations
import tkinter as tk
import webbrowser
from constants import APP_NAME, APP_VERSION, COLORS, DONATE_URL
from ui.image_service import load_image

class SplashScreen(tk.Toplevel):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg="#07111A")
        self.geometry("560x690")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 560) // 2
        y = (self.winfo_screenheight() - 690) // 2
        self.geometry(f"560x690+{x}+{y}")

        frame = tk.Frame(self, bg="#07111A", highlightbackground=COLORS["teal"], highlightthickness=2)
        frame.pack(fill="both", expand=True)

        logo = load_image("hamradio-pi-logo.png", 360, 360)
        if logo:
            label = tk.Label(frame, image=logo, bg="#07111A")
            label.image = logo
            label.pack(pady=(22, 6))

        tk.Label(frame, text=APP_NAME, bg="#07111A", fg=COLORS["text"],
                 font=("DejaVu Sans", 22, "bold")).pack()
        tk.Label(frame, text="Ham Shack Control Centre for Raspberry Pi",
                 bg="#07111A", fg=COLORS["muted"], font=("DejaVu Sans", 11)).pack(pady=(4, 14))

        self.status = tk.StringVar(value="Starting up…")
        tk.Label(frame, textvariable=self.status, bg="#07111A", fg=COLORS["text"],
                 font=("DejaVu Sans", 11)).pack()

        self.canvas = tk.Canvas(frame, width=390, height=18, bg="#07111A",
                                highlightbackground=COLORS["teal_dark"], highlightthickness=1)
        self.canvas.pack(pady=(12, 6))
        self.bar = self.canvas.create_rectangle(0, 0, 0, 18, fill=COLORS["teal_dark"], width=0)

        tk.Label(frame, text=f"Version {APP_VERSION}", bg="#07111A", fg=COLORS["muted"],
                 font=("DejaVu Sans", 9)).pack(pady=(0, 12))

        donate = tk.Frame(frame, bg="#111923", highlightbackground="#C99B16", highlightthickness=1)
        donate.pack(fill="x", padx=22, pady=(4, 20))
        tk.Label(donate, text="Support HamRadio-Pi Ultimate",
                 bg="#111923", fg="#FFD55A", font=("DejaVu Sans", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
        tk.Label(donate, text="If you find this project useful, please consider helping support development.",
                 bg="#111923", fg=COLORS["text"], justify="left",
                 font=("DejaVu Sans", 9), wraplength=360).pack(anchor="w", padx=14)
        row = tk.Frame(donate, bg="#111923")
        row.pack(fill="x", padx=14, pady=10)
        tk.Button(row, text="Donate", command=lambda: webbrowser.open(DONATE_URL),
                  bg="#F4C430", fg="#111111", activebackground="#FFD95B",
                  activeforeground="#111111", relief="flat", bd=0,
                  padx=24, pady=8, cursor="hand2",
                  font=("DejaVu Sans", 11, "bold")).pack(side="left")
        tk.Label(row, text="Minimum $1 USD", bg="#111923", fg="#FFD55A",
                 font=("DejaVu Sans", 9, "bold")).pack(side="left", padx=14)

    def set_progress(self, percent: int, text: str) -> None:
        self.status.set(text)
        self.canvas.coords(self.bar, 0, 0, 3.9 * max(0, min(100, percent)), 18)
        self.update_idletasks()
