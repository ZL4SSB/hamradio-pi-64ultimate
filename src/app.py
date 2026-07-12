#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox

from constants import APP_NAME, BASE_DIR
from qt_app.theme import APP_QSS
from qt_app.splash import SplashDialog
from qt_app.main_window import MainWindow


def write_startup_error(exc: BaseException) -> str:
    log_dir = BASE_DIR / "reports"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "startup-error.log"
    path.write_text(
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        encoding="utf-8",
    )
    return str(path)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(APP_QSS)

    splash = SplashDialog()
    splash.show()
    splash.update_stage(15, "Loading interface…")

    window_holder = {}

    QTimer.singleShot(350, lambda: splash.update_stage(45, "Loading services…"))
    QTimer.singleShot(700, lambda: splash.update_stage(75, "Preparing dashboard…"))

    def launch():
        splash.update_stage(100, "Ready")
        try:
            window = MainWindow()
            window_holder["window"] = window
            window.show()
            splash.close()
        except Exception as exc:
            log_path = write_startup_error(exc)
            splash.close()
            QMessageBox.critical(
                None,
                "HamRadio-Pi Ultimate startup error",
                f"The main window could not start.\n\n"
                f"{type(exc).__name__}: {exc}\n\n"
                f"Full details were saved to:\n{log_path}",
            )
            app.quit()

    QTimer.singleShot(1100, launch)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
