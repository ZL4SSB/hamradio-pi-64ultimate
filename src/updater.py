#!/usr/bin/env python3

"""
HamRadio-Pi Ultimate
Safe Git Updater
Version 0.3.2

The updater:
- Confirms the project is a Git clone.
- Refuses to overwrite uncommitted work.
- Backs up personal configuration.
- Fetches the latest main branch from GitHub.
- Applies only a fast-forward update.
- Records the previous commit for rollback.
- Restores personal configuration after updating.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
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
    """Raised when an update cannot continue safely."""


class GitUpdater:
    """Performs safe, fast-forward-only Git updates."""

    def __init__(self, log_callback) -> None:
        self.log = log_callback

    @staticmethod
    def run_git(*arguments: str, check: bool = True) -> str:
        """Run Git in the project directory and return standard output."""

        command = ["git", *arguments]

        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_DIR,
                text=True,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError as error:
            raise UpdateError(
                "Git is not installed or cannot be found."
            ) from error

        if check and result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise UpdateError(message or "Git command failed.")

        return result.stdout.strip()

    def verify_repository(self) -> None:
        """Confirm this project is an intact Git repository."""

        git_dir = PROJECT_DIR / ".git"

        if not git_dir.exists():
            raise UpdateError(
                "This installation is not a Git clone.\n\n"
                "Clone the official GitHub repository before using "
                "the automatic updater."
            )

        repository_root = Path(
            self.run_git("rev-parse", "--show-toplevel")
        ).resolve()

        if repository_root != PROJECT_DIR.resolve():
            raise UpdateError(
                "The updater is not running from the expected "
                "Git repository."
            )

    def verify_clean_worktree(self) -> None:
        """Protect local edits from being overwritten."""

        status = self.run_git("status", "--porcelain")

        if status:
            raise UpdateError(
                "The project contains uncommitted changes.\n\n"
                "Commit, push, or discard those changes before updating.\n\n"
                "Git status:\n"
                f"{status}"
            )

    def current_commit(self) -> str:
        """Return the current commit identifier."""

        return self.run_git("rev-parse", "HEAD")

    def current_branch(self) -> str:
        """Return the current branch name."""

        return self.run_git("branch", "--show-current")

    def create_backup(self) -> Path:
        """Back up user-specific configuration files."""

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = BACKUP_ROOT / timestamp
        backup_dir.mkdir(parents=True, exist_ok=False)

        copied = 0

        for source in PERSONAL_FILES:
            if not source.exists():
                continue

            destination = backup_dir / source.name
            shutil.copy2(source, destination)
            copied += 1
            self.log(f"Backed up {source.name}")

        manifest = {
            "created": datetime.now().isoformat(timespec="seconds"),
            "project": str(PROJECT_DIR),
            "files_copied": copied,
        }

        with (backup_dir / "backup.json").open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(manifest, file, indent=4)

        return backup_dir

    def restore_backup(self, backup_dir: Path) -> None:
        """Restore personal files after an update or rollback."""

        for source in backup_dir.glob("*.json"):
            if source.name == "backup.json":
                continue

            destination = CONFIG_DIR / source.name
            shutil.copy2(source, destination)
            self.log(f"Restored {source.name}")

    def fetch(self) -> None:
        """Fetch current information from GitHub."""

        self.log("Contacting GitHub...")
        self.run_git("fetch", "--prune", "origin")

    def commits_behind(self, branch: str) -> int:
        """Return how many commits the local branch is behind GitHub."""

        output = self.run_git(
            "rev-list",
            "--count",
            f"HEAD..origin/{branch}",
        )

        return int(output or "0")

    def commits_ahead(self, branch: str) -> int:
        """Return how many local commits have not been pushed."""

        output = self.run_git(
            "rev-list",
            "--count",
            f"origin/{branch}..HEAD",
        )

        return int(output or "0")

    def update(self) -> tuple[bool, str]:
        """Run a complete safe update."""

        self.verify_repository()
        self.verify_clean_worktree()

        branch = self.current_branch()

        if not branch:
            raise UpdateError(
                "The repository is in detached HEAD mode. "
                "Switch back to the main branch before updating."
            )

        self.fetch()

        ahead = self.commits_ahead(branch)

        if ahead:
            raise UpdateError(
                f"This computer has {ahead} local commit(s) that "
                "have not been pushed.\n\n"
                "Push them to GitHub before updating."
            )

        behind = self.commits_behind(branch)

        if behind == 0:
            return False, "HamRadio-Pi Ultimate is already up to date."

        old_commit = self.current_commit()
        backup_dir = self.create_backup()

        self.log(
            f"Downloading {behind} update commit(s) from GitHub..."
        )

        try:
            self.run_git("pull", "--ff-only", "origin", branch)
            self.restore_backup(backup_dir)
        except Exception:
            self.log("Update failed. Restoring the previous version...")
            self.run_git("reset", "--hard", old_commit, check=False)
            self.restore_backup(backup_dir)
            raise

        new_commit = self.current_commit()

        rollback_data = {
            "previous_commit": old_commit,
            "updated_commit": new_commit,
            "branch": branch,
            "backup_directory": str(backup_dir),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with ROLLBACK_FILE.open("w", encoding="utf-8") as file:
            json.dump(rollback_data, file, indent=4)

        return True, (
            f"Update complete.\n\n"
            f"Installed {behind} new commit(s).\n"
            f"Previous version: {old_commit[:8]}\n"
            f"Current version: {new_commit[:8]}"
        )

    def rollback(self) -> str:
        """Return to the commit stored by the last successful update."""

        if not ROLLBACK_FILE.exists():
            raise UpdateError(
                "No previous automatic update is available to restore."
            )

        with ROLLBACK_FILE.open("r", encoding="utf-8") as file:
            rollback_data = json.load(file)

        previous_commit = rollback_data.get("previous_commit")
        backup_directory = rollback_data.get("backup_directory")

        if not previous_commit:
            raise UpdateError("The rollback information is incomplete.")

        self.verify_repository()
        self.verify_clean_worktree()

        self.log(
            f"Restoring previous version {previous_commit[:8]}..."
        )

        self.run_git("reset", "--hard", previous_commit)

        if backup_directory:
            backup_dir = Path(backup_directory)

            if backup_dir.exists():
                self.restore_backup(backup_dir)

        return (
            "The previous version has been restored.\n\n"
            "Restart HamRadio-Pi Ultimate."
        )


class UpdaterWindow:
    """Graphical update and rollback window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HamRadio-Pi Ultimate - Updates")
        self.root.geometry("760x560")
        self.root.minsize(650, 480)

        self.status_value = tk.StringVar(
            value="Ready to check GitHub for updates."
        )

        self.updater = GitUpdater(self.write_log)
        self.build_interface()

    def build_interface(self) -> None:
        """Create the updater interface."""

        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="HamRadio-Pi Ultimate",
            font=("Arial", 22, "bold"),
        ).pack()

        ttk.Label(
            main,
            text="Update Manager",
            font=("Arial", 15),
        ).pack(pady=(2, 15))

        version_frame = ttk.LabelFrame(
            main,
            text="Installed Version",
            padding=12,
        )
        version_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(
            version_frame,
            text=self.read_version(),
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main,
            textvariable=self.status_value,
            wraplength=700,
            justify="left",
        ).pack(fill="x", pady=(0, 12))

        self.log_box = scrolledtext.ScrolledText(
            main,
            height=16,
            state="disabled",
            wrap="word",
        )
        self.log_box.pack(fill="both", expand=True)

        button_frame = ttk.Frame(main)
        button_frame.pack(fill="x", pady=(14, 0))

        self.rollback_button = ttk.Button(
            button_frame,
            text="Restore Previous Version",
            command=self.start_rollback,
        )
        self.rollback_button.pack(side="left")

        self.update_button = ttk.Button(
            button_frame,
            text="Check and Install Updates",
            command=self.start_update,
        )
        self.update_button.pack(side="right")

        ttk.Button(
            button_frame,
            text="Close",
            command=self.root.destroy,
        ).pack(side="right", padx=(0, 10))

    @staticmethod
    def read_version() -> str:
        """Read the human-facing application version."""

        if not VERSION_FILE.exists():
            return "Version information not found"

        try:
            with VERSION_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return "Version information could not be read"

        version = data.get("version", "Unknown")
        edition = data.get("edition", "Community")

        return f"HamRadio-Pi Ultimate {edition} Edition — {version}"

    def write_log(self, message: str) -> None:
        """Append text to the updater log."""

        def append() -> None:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        self.root.after(0, append)

    def set_busy(self, busy: bool) -> None:
        """Enable or disable updater controls."""

        state = "disabled" if busy else "normal"
        self.update_button.configure(state=state)
        self.rollback_button.configure(state=state)

    def start_update(self) -> None:
        """Run the update without freezing the window."""

        self.set_busy(True)
        self.status_value.set("Checking GitHub...")

        thread = threading.Thread(
            target=self.perform_update,
            daemon=True,
        )
        thread.start()

    def perform_update(self) -> None:
        """Worker method for updating."""

        try:
            changed, message = self.updater.update()
        except (UpdateError, OSError, json.JSONDecodeError) as error:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Update failed",
                    str(error),
                ),
            )
            self.root.after(
                0,
                lambda: self.status_value.set("Update failed."),
            )
        else:
            self.root.after(
                0,
                lambda: self.status_value.set(message),
            )

            if changed:
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Update complete",
                        message
                        + "\n\nClose and restart "
                        "HamRadio-Pi Ultimate.",
                    ),
                )
            else:
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "No update needed",
                        message,
                    ),
                )
        finally:
            self.root.after(0, lambda: self.set_busy(False))

    def start_rollback(self) -> None:
        """Confirm and start a rollback."""

        confirmed = messagebox.askyesno(
            "Restore previous version",
            "Restore the version from before the last automatic "
            "update?\n\n"
            "Personal station settings will be preserved.",
        )

        if not confirmed:
            return

        self.set_busy(True)
        self.status_value.set("Restoring the previous version...")

        thread = threading.Thread(
            target=self.perform_rollback,
            daemon=True,
        )
        thread.start()

    def perform_rollback(self) -> None:
        """Worker method for rollback."""

        try:
            message = self.updater.rollback()
        except (UpdateError, OSError, json.JSONDecodeError) as error:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Restore failed",
                    str(error),
                ),
            )
            self.root.after(
                0,
                lambda: self.status_value.set("Restore failed."),
            )
        else:
            self.root.after(
                0,
                lambda: self.status_value.set(message),
            )
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Previous version restored",
                    message,
                ),
            )
        finally:
            self.root.after(0, lambda: self.set_busy(False))


def main() -> None:
    """Start the graphical update manager."""

    root = tk.Tk()
    UpdaterWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
