#!/usr/bin/env python3
import sys
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from constants import APP_NAME
from qt_app.theme import APP_QSS
from qt_app.splash import SplashDialog
from qt_app.main_window import MainWindow

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(APP_QSS)

    splash = SplashDialog()
    splash.show()
    splash.update_stage(15, "Loading interface…")

    window_holder = {}

    def stage_two():
        splash.update_stage(45, "Loading services…")

    def stage_three():
        splash.update_stage(75, "Preparing dashboard…")

    def launch():
        splash.update_stage(100, "Ready")
        try:
            window = MainWindow()
            window_holder["window"] = window
            window.show()
            splash.close()
        except Exception as exc:
            splash.close()
            QMessageBox.critical(
                None,
                "HamRadio-Pi Ultimate startup error",
                f"The main window could not start.\n\n{type(exc).__name__}: {exc}"
            )
            app.quit()

    QTimer.singleShot(350, stage_two)
    QTimer.singleShot(700, stage_three)
    QTimer.singleShot(1100, launch)
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
