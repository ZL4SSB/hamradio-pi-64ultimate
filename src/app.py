#!/usr/bin/env python3

import os

# This must be set before importing PyQt6. It avoids the optional Windows
# native Qt Quick Controls plugin that may be missing from pip installations.
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

import argparse
import sys
import traceback

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtWidgets import QApplication, QMessageBox

from backend import Backend
from constants import APP_NAME, ASSETS_DIR, BASE_DIR, REPORTS_DIR


def parse_args():
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--no-splash", action="store_true")
    return parser.parse_args()


def write_error(text: str) -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / "qml-startup-error.log"
    path.write_text(text + "\n", encoding="utf-8")
    return str(path)


def main() -> int:
    args = parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(
        QIcon(str(ASSETS_DIR / "branding" / "hamradio-pi-256.png"))
    )

    backend = Backend()
    engines: list[QQmlApplicationEngine] = []
    splash_engine: QQmlApplicationEngine | None = None

    def load_engine(path, warnings):
        engine = QQmlApplicationEngine()
        engines.append(engine)
        engine.rootContext().setContextProperty("backend", backend)
        engine.warnings.connect(
            lambda items: warnings.extend(item.toString() for item in items)
        )
        engine.load(QUrl.fromLocalFile(str(path)))
        return engine

    def show_error(messages: list[str]):
        text = "\n".join(messages) or "The QML engine returned no window."
        log_path = write_error(text)
        QMessageBox.critical(
            None,
            APP_NAME,
            f"The QML interface could not start.\n\n{text}\n\n"
            f"Full log:\n{log_path}",
        )
        app.quit()

    def close_splash():
        nonlocal splash_engine
        if splash_engine is None:
            return
        for item in splash_engine.rootObjects():
            item.close()
        splash_engine.deleteLater()
        splash_engine = None
        app.processEvents()

    def load_main():
        warnings: list[str] = []
        path = BASE_DIR / "src" / "qml" / "Main.qml"
        try:
            engine = load_engine(path, warnings)
        except Exception:
            warnings.append(traceback.format_exc())
            close_splash()
            show_error(warnings)
            return

        if not engine.rootObjects():
            close_splash()
            warnings.append(f"Could not load: {path}")
            show_error(warnings)
            return

        close_splash()
        app.setQuitOnLastWindowClosed(True)

    if args.no_splash:
        QTimer.singleShot(0, load_main)
    else:
        warnings: list[str] = []
        splash_path = BASE_DIR / "src" / "qml" / "Splash.qml"
        splash_engine = load_engine(splash_path, warnings)
        if not splash_engine.rootObjects():
            show_error(warnings + [f"Could not load: {splash_path}"])
        else:
            QTimer.singleShot(850, load_main)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
