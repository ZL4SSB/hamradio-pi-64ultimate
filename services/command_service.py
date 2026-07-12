from __future__ import annotations

import subprocess
import threading
import tkinter as tk
from typing import Callable, Optional


class CommandRunner:
    def __init__(self, root: tk.Misc, output_callback: Callable[[str], None]) -> None:
        self.root = root
        self.output_callback = output_callback
        self.running = False

    def run(self, command: list[str], on_finish: Optional[Callable[[int], None]] = None) -> bool:
        if self.running:
            self.output_callback("Another task is already running.")
            return False

        self.running = True

        def worker() -> None:
            return_code = 1
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                if process.stdout:
                    for line in process.stdout:
                        self.root.after(0, self.output_callback, line.rstrip())
                return_code = process.wait()
            except Exception as exc:
                self.root.after(0, self.output_callback, f"ERROR: {exc}")
            finally:
                self.running = False
                if on_finish:
                    self.root.after(0, on_finish, return_code)

        threading.Thread(target=worker, daemon=True).start()
        return True
