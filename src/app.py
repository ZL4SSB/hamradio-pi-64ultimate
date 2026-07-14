#!/usr/bin/env python3

import os

# Must be set before importing PyQt6. This avoids optional platform style
# plugins and makes the same QML controls work on Windows and Raspberry Pi.
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

import argparse
import json
import sys
from pathlib import Path
import traceback

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtWidgets import QApplication, QMessageBox

try:
    from PyQt6.QtWebEngineQuick import QtWebEngineQuick
except ImportError:
    QtWebEngineQuick = None

from backend import Backend
from constants import APP_NAME, ASSETS_DIR, BASE_DIR, CONFIG_DIR, REPORTS_DIR


def parse_args():
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--no-splash", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def show_splash_setting() -> bool:
    try:
        settings = json.loads(
            (CONFIG_DIR / "settings.json").read_text(encoding="utf-8")
        )
        return bool(settings.get("show_splash", True))
    except Exception:
        return True


def write_error(text: str) -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / "qml-startup-error.log"
    path.write_text(text + "\n", encoding="utf-8")
    return str(path)


def main() -> int:
    args = parse_args()

    if QtWebEngineQuick is not None:
        QtWebEngineQuick.initialize()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(
        QIcon(str(ASSETS_DIR / "branding" / "hamradio-pi-256.png"))
    )

    backend = Backend()

    startup_steps = [
        (8, "Loading station profile"),
        (18, "Loading application catalogue"),
        (30, "Checking hardware services"),
        (42, "Preparing audio devices"),
        (55, "Starting local propagation server"),
        (68, "Loading radio dashboards"),
        (80, "Preparing Station Tools"),
        (90, "Checking saved preferences"),
        (100, "Ready"),
    ]
    startup_step_index = 0

    def advance_startup():
        nonlocal startup_step_index
        if startup_step_index >= len(startup_steps):
            return
        progress, stage = startup_steps[startup_step_index]
        backend.setStartupProgress(progress, stage)
        startup_step_index += 1
        if startup_step_index < len(startup_steps):
            QTimer.singleShot(480, advance_startup)

    QTimer.singleShot(120, advance_startup)

    app.aboutToQuit.connect(
        lambda: (
            backend.stopPropagationServer()
            if sys.platform.startswith("win")
            else None
        )
    )
    engines: list[QQmlApplicationEngine] = []
    splash_engine: QQmlApplicationEngine | None = None
    main_loaded = False

    def load_engine(path, warnings):
        engine = QQmlApplicationEngine()
        engines.append(engine)
        engine.rootContext().setContextProperty("backend", backend)
        engine.warnings.connect(
            lambda items: warnings.extend(item.toString() for item in items)
        )
        engine.load(QUrl.fromLocalFile(str(path)))
        return engine

    def show_error(messages):
        text = "\n".join(messages) or "The QML engine returned no window."
        path = write_error(text)
        QMessageBox.critical(
            None,
            APP_NAME,
            f"The interface could not start.\n\n{text}\n\nFull log:\n{path}",
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
        nonlocal main_loaded
        if main_loaded:
            return
        main_loaded = True

        warnings: list[str] = []
        qml_path = BASE_DIR / "src" / "qml" / "Main.qml"

        try:
            engine = load_engine(qml_path, warnings)
        except Exception:
            warnings.append(traceback.format_exc())
            close_splash()
            show_error(warnings)
            return

        if not engine.rootObjects():
            close_splash()
            warnings.append(f"Could not load: {qml_path}")
            show_error(warnings)
            return

        close_splash()
        app.setQuitOnLastWindowClosed(True)

        if backend.autoScan:
            QTimer.singleShot(1200, backend.scanHardware)

        if backend.checkUpdates:
            QTimer.singleShot(1800, backend.checkForUpdates)

        if args.self_test:
            QTimer.singleShot(900, app.quit)

    use_splash = not args.no_splash and show_splash_setting()

    if use_splash:
        warnings: list[str] = []
        splash_path = BASE_DIR / "src" / "qml" / "Splash.qml"
        splash_engine = load_engine(splash_path, warnings)

        if not splash_engine.rootObjects():
            show_error(warnings + [f"Could not load: {splash_path}"])
        else:
            backend.skipSplashRequested.connect(load_main)
            QTimer.singleShot(5000, load_main)
    else:
        QTimer.singleShot(0, load_main)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
