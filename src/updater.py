#!/usr/bin/env python3

import json
import shutil
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_DIR / "config"
VERSION_FILE = CONFIG_DIR / "version.json"
BACKUP_ROOT = PROJECT_DIR / "backups"
ROLLBACK_FILE = CONFIG_DIR / "rollback.json"

PERSONAL_FILES = (
    CONFIG_DIR / "station.json",
    CONFIG_DIR / "settings.json",
    CONFIG_DIR / "favourites.json",
    CONFIG_DIR / "installed_apps.json",
)

class UpdateError(RuntimeError):
    pass

class GitUpdater:
    def __init__(self, log_callback) -> None:
        self.log = log_callback

    @staticmethod
    def git(*args: str, check: bool = True) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=PROJECT_DIR,
                text=True,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError as error:
            raise UpdateError("Git is not installed or cannot be found.") from error

        if check and result.returncode != 0:
            raise UpdateError(result.stderr.strip() or result.stdout.strip() or "Git command failed.")
        return result.stdout.strip()

    def verify(self) -> None:
        if not (PROJECT_DIR / ".git").exists():
            raise UpdateError("This installation is not a Git clone.")
        if self.git("status", "--porcelain"):
            raise UpdateError("Commit or discard local changes before updating.")

    def backup(self) -> Path:
        folder = BACKUP_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S")
        folder.mkdir(parents=True, exist_ok=False)
        for source in PERSONAL_FILES:
            if source.exists():
                shutil.copy2(source, folder / source.name)
                self.log(f"Backed up {source.name}")
        return folder

    def restore(self, folder: Path) -> None:
        for source in folder.glob("*.json"):
            shutil.copy2(source, CONFIG_DIR / source.name)
            self.log(f"Restored {source.name}")

    def update(self) -> str:
        self.verify()
        branch = self.git("branch", "--show-current")
        old_commit = self.git("rev-parse", "HEAD")
        self.git("fetch", "--prune", "origin")
        behind = int(self.git("rev-list", "--count", f"HEAD..origin/{branch}") or "0")
        if behind == 0:
            return "HamRadio-Pi Ultimate is already up to date."

        backup = self.backup()
        self.git("pull", "--ff-only", "origin", branch)
        self.restore(backup)
        new_commit = self.git("rev-parse", "HEAD")
        ROLLBACK_FILE.write_text(json.dumps({
            "previous_commit": old_commit,
            "updated_commit": new_commit,
            "backup_directory": str(backup),
        }, indent=4) + "\n", encoding="utf-8")
        return f"Update complete. Installed {behind} new commit(s)."

class UpdaterWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Updates")
        self.root.geometry("720x520")
        self.status = tk.StringVar(value="Ready to check GitHub.")
        self.updater = GitUpdater(self.log)
        self.build()

    def build(self) -> None:
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)
        ttk.Label(main, text="HamRadio-Pi Ultimate", font=("Arial", 22, "bold")).pack()
        ttk.Label(main, text="Update Manager", font=("Arial", 15)).pack(pady=(2, 15))
        ttk.Label(main, textvariable=self.status).pack(fill="x")
        self.box = scrolledtext.ScrolledText(main, state="disabled", height=16)
        self.box.pack(fill="both", expand=True, pady=12)
        ttk.Button(main, text="Check and Install Updates", command=self.start).pack(side="right")

    def log(self, text: str) -> None:
        def append():
            self.box.configure(state="normal")
            self.box.insert("end", text + "\n")
            self.box.configure(state="disabled")
        self.root.after(0, append)

    def start(self) -> None:
        threading.Thread(target=self.run_update, daemon=True).start()

    def run_update(self) -> None:
        try:
            result = self.updater.update()
        except UpdateError as error:
            self.root.after(0, lambda: messagebox.showerror("Update failed", str(error)))
        else:
            self.root.after(0, lambda: self.status.set(result))
            self.root.after(0, lambda: messagebox.showinfo("Updates", result))

def main() -> None:
    root = tk.Tk()
    UpdaterWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
