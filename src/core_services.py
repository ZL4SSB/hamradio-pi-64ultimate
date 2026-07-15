from __future__ import annotations

import json
import math
import shutil
import sqlite3
import subprocess
import threading
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


def band_from_frequency(frequency_hz: int) -> str:
    mhz = frequency_hz / 1_000_000.0
    ranges = [
        (1.8, 2.0, "160 m"),
        (3.5, 4.0, "80 m"),
        (5.0, 5.5, "60 m"),
        (7.0, 7.3, "40 m"),
        (10.1, 10.15, "30 m"),
        (14.0, 14.35, "20 m"),
        (18.068, 18.168, "17 m"),
        (21.0, 21.45, "15 m"),
        (24.89, 24.99, "12 m"),
        (28.0, 29.7, "10 m"),
        (50.0, 54.0, "6 m"),
        (144.0, 148.0, "2 m"),
        (430.0, 450.0, "70 cm"),
    ]
    for low, high, label in ranges:
        if low <= mhz <= high:
            return label
    return "Out of band"


@dataclass
class RadioState:
    radio_id: str = "default"
    radio_name: str = "No radio connected"
    frequency_hz: int = 14_074_000
    mode: str = "USB-D"
    ptt: bool = False
    split: bool = False
    vfo: str = "A"
    rit_hz: int = 0
    xit_hz: int = 0
    power_w: int = 10
    cat_connected: bool = False
    cat_backend: str = "Disconnected"
    cat_port: str = ""
    audio_rx: str = ""
    audio_tx: str = ""
    audio_routing: str = "Radio profile"
    sample_rate: int = 48000
    rx_channel: str = "Mono Mix"
    tx_channel: str = "Mono Mix"
    rx_gain_db: float = 0.0
    tx_level: int = 50
    rotator_azimuth: float = 0.0
    rotator_elevation: float = 0.0

    @property
    def band(self) -> str:
        return band_from_frequency(self.frequency_hz)

    def to_dict(self) -> dict:
        value = asdict(self)
        value["band"] = self.band
        value["frequency"] = f"{self.frequency_hz / 1_000_000:.6f}"
        value["ptt_label"] = "TX" if self.ptt else "RX"
        return value


class RadioStateService:
    def __init__(self) -> None:
        self.state = RadioState()
        self._lock = threading.RLock()
        self._subscribers: list = []

    def subscribe(self, callback) -> None:
        """Subscribe a module to authoritative station-state snapshots."""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def _publish(self) -> dict:
        snapshot = self.state.to_dict()
        for callback in tuple(self._subscribers):
            callback(dict(snapshot))
        return snapshot

    def set_frequency_mhz(self, mhz: float) -> dict:
        hz = int(round(max(0.0, mhz) * 1_000_000))
        self.state.frequency_hz = hz
        return self._publish()

    def set_mode(self, mode: str) -> dict:
        allowed = {
            "LSB", "USB", "CW", "CW-R", "AM", "FM",
            "USB-D", "LSB-D", "DIGU", "DIGL",
        }
        clean = mode.strip().upper()
        if clean in allowed:
            self.state.mode = clean
        return self._publish()

    def set_ptt(self, active: bool) -> dict:
        self.state.ptt = bool(active)
        return self._publish()

    def set_split(self, active: bool) -> dict:
        self.state.split = bool(active)
        return self._publish()

    def configure_audio(
        self,
        rx_device: str,
        tx_device: str,
        rx_channel: str,
        tx_channel: str,
        rx_gain_db: float,
        tx_level: int,
    ) -> dict:
        self.state.audio_rx = rx_device.strip()
        self.state.audio_tx = tx_device.strip()
        self.state.rx_channel = rx_channel
        self.state.tx_channel = tx_channel
        self.state.rx_gain_db = max(-30.0, min(30.0, float(rx_gain_db)))
        self.state.tx_level = max(0, min(100, int(tx_level)))
        return self._publish()

    def set_vfo(self, vfo: str) -> dict:
        clean = vfo.strip().upper()
        if clean in {"A", "B"}:
            self.state.vfo = clean
        return self._publish()

    def set_offsets(self, rit_hz: int, xit_hz: int) -> dict:
        self.state.rit_hz = max(-9999, min(9999, int(rit_hz)))
        self.state.xit_hz = max(-9999, min(9999, int(xit_hz)))
        return self._publish()


class CatBroker:
    """HRPU-owned CAT broker boundary.

    This service intentionally does not copy a CAT implementation from another
    amateur-radio program. It detects Hamlib utilities and can poll a configured
    rigctld TCP endpoint. Physical-radio ownership remains in HRPU.
    """

    def __init__(self, radio: RadioStateService) -> None:
        self.radio = radio
        self.status = "Stopped"
        self.detail = "No CAT backend connected"
        self.clients: list[dict] = []
        self.host = "127.0.0.1"
        self.port = 4532
        self.polling = False
        self.reconnect_attempts = 0

    def snapshot(self) -> dict:
        return {
            "status": self.status,
            "detail": self.detail,
            "host": self.host,
            "port": self.port,
            "hamlib_available": bool(shutil.which("rigctl") or shutil.which("rigctld")),
            "clients": list(self.clients),
            "polling": self.polling,
            "reconnect_attempts": self.reconnect_attempts,
        }

    def probe(self) -> dict:
        rigctl = shutil.which("rigctl")
        rigctld = shutil.which("rigctld")
        if rigctl or rigctld:
            self.detail = "Hamlib utilities detected"
            self.status = "Ready"
            self.radio.state.cat_backend = "Hamlib"
        else:
            self.detail = "Hamlib not detected; broker remains in preview mode"
            self.status = "Preview"
            self.radio.state.cat_backend = "Preview"
        return self.snapshot()

    def register_client(self, name: str) -> dict:
        clean = name.strip()
        if clean and not any(row["name"] == clean for row in self.clients):
            self.clients.append({
                "name": clean,
                "connected": True,
                "since": datetime.now().strftime("%H:%M:%S"),
            })
        return self.snapshot()

    def disconnect(self, reason: str = "Stopped by operator") -> dict:
        self.status = "Stopped"
        self.detail = reason
        self.polling = False
        self.radio.state.cat_connected = False
        return self.snapshot()

    def note_reconnect(self) -> dict:
        self.reconnect_attempts += 1
        self.status = "Reconnecting"
        self.detail = f"Reconnect attempt {self.reconnect_attempts}"
        return self.snapshot()


class LogbookService:
    def __init__(self, database_path: Path) -> None:
        self.path = database_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.path)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialise(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS qso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    utc TEXT NOT NULL,
                    callsign TEXT NOT NULL,
                    grid TEXT,
                    frequency_hz INTEGER NOT NULL,
                    band TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    rst_sent TEXT,
                    rst_received TEXT,
                    notes TEXT
                )
                """
            )

    def add(
        self,
        callsign: str,
        grid: str,
        frequency_hz: int,
        mode: str,
        rst_sent: str,
        rst_received: str,
        notes: str,
    ) -> dict:
        call = callsign.strip().upper()
        if not call:
            raise ValueError("Callsign is required")
        utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        band = band_from_frequency(frequency_hz)
        with self._connect() as db:
            cursor = db.execute(
                """
                INSERT INTO qso
                (utc, callsign, grid, frequency_hz, band, mode,
                 rst_sent, rst_received, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc,
                    call,
                    grid.strip().upper(),
                    frequency_hz,
                    band,
                    mode,
                    rst_sent.strip(),
                    rst_received.strip(),
                    notes.strip(),
                ),
            )
            qso_id = cursor.lastrowid
        return {"id": qso_id, "callsign": call, "band": band, "mode": mode}

    def recent(self, limit: int = 100) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                """
                SELECT id, utc, callsign, grid, frequency_hz, band, mode,
                       rst_sent, rst_received, notes
                FROM qso ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def export_adif(self, path: Path) -> Path:
        rows = list(reversed(self.recent(100000)))
        lines = ["Generated by HamRadio-Pi Ultimate", "<EOH>"]
        for row in rows:
            date, clock = row["utc"].split(" ", 1)
            record = [
                f"<QSO_DATE:8>{date.replace('-', '')}",
                f"<TIME_ON:6>{clock.replace(':', '')}",
                f"<CALL:{len(row['callsign'])}>{row['callsign']}",
                f"<BAND:{len(row['band'])}>{row['band']}",
                f"<MODE:{len(row['mode'])}>{row['mode']}",
            ]
            if row["grid"]:
                record.append(f"<GRIDSQUARE:{len(row['grid'])}>{row['grid']}")
            if row["rst_sent"]:
                record.append(f"<RST_SENT:{len(row['rst_sent'])}>{row['rst_sent']}")
            if row["rst_received"]:
                record.append(f"<RST_RCVD:{len(row['rst_received'])}>{row['rst_received']}")
            record.append("<EOR>")
            lines.append(" ".join(record))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


class DigitalWorkspaceService:
    MODES = ["FT8", "FT4", "FT2", "Q65", "MSK144", "FST4", "FST4W", "WSPR"]

    def __init__(self) -> None:
        self.mode = "FT8"
        self.tx_enabled = False
        self.auto_sequence = False
        self.decoded: list[dict] = []
        self.selected_call = ""
        self.status = "Digital engine boundary ready; no decoder loaded"

    def snapshot(self) -> dict:
        return {
            "mode": self.mode,
            "modes": self.MODES,
            "tx_enabled": self.tx_enabled,
            "auto_sequence": self.auto_sequence,
            "selected_call": self.selected_call,
            "status": self.status,
            "decoded": list(self.decoded),
        }

    def demo_decode(self) -> dict:
        samples = [
            ("G4ABC", "IO91", -12, "CQ G4ABC IO91"),
            ("JA1XYZ", "PM95", -18, "JA1XYZ ZL4SSB -18"),
            ("VK3ABC", "QF22", -6, "CQ VK3ABC QF22"),
            ("W6WX", "CM97", -15, "W6WX ZL4SSB R-15"),
        ]
        self.decoded = [
            {
                "utc": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                "call": call,
                "grid": grid,
                "snr": snr,
                "message": message,
                "mode": self.mode,
            }
            for call, grid, snr, message in samples
        ]
        self.status = "Preview decode activity loaded — not live RF decoding"
        return self.snapshot()


class SatelliteRotatorService:
    def __init__(self) -> None:
        self.target = "No satellite selected"
        self.azimuth = 0.0
        self.elevation = 0.0
        self.doppler_hz = 0
        self.tracking = False
        self.rotator_connected = False
        self.status = "Satellite/rotator framework ready"

    def snapshot(self) -> dict:
        return {
            "target": self.target,
            "azimuth": round(self.azimuth, 1),
            "elevation": round(self.elevation, 1),
            "doppler_hz": self.doppler_hz,
            "tracking": self.tracking,
            "rotator_connected": self.rotator_connected,
            "status": self.status,
        }

    def select_preview(self, target: str) -> dict:
        presets = {
            "ISS": (42.0, 28.0, -2850),
            "AO-91": (327.0, 16.5, 4120),
            "SO-50": (114.0, 34.2, -5100),
        }
        self.target = target
        self.azimuth, self.elevation, self.doppler_hz = presets.get(
            target, (0.0, 0.0, 0)
        )
        self.status = "Preview geometry — live TLE adapter not configured"
        return self.snapshot()
