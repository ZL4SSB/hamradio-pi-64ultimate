#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import socket
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
PREFIX_PATH = ROOT / "data" / "prefixes.json"

SPOT_RE = re.compile(
    r"DX de\s+([A-Z0-9/]+)[-:# ]+\s*([0-9.]+)\s+"
    r"([A-Z0-9/]+)\s*(.*?)\s+(\d{4})Z",
    re.I,
)

BANDS = [
    (1800, 2000, "160m"),
    (3500, 4000, "80m"),
    (5000, 5500, "60m"),
    (7000, 7300, "40m"),
    (10100, 10150, "30m"),
    (14000, 14350, "20m"),
    (18068, 18168, "17m"),
    (21000, 21450, "15m"),
    (24890, 24990, "12m"),
    (28000, 29700, "10m"),
    (50000, 54000, "6m"),
]


@dataclass
class Spot:
    id: str
    timestamp: str
    reporter: str
    dx: str
    frequency_khz: float
    band: str
    comment: str
    source_lat: float
    source_lon: float
    source_name: str
    target_lat: float
    target_lon: float
    target_name: str


def load_config() -> dict:
    default = {
        "server": {"host": "127.0.0.1", "port": 8765},
        "station": {
            "callsign": "",
            "locator": "",
            "latitude": None,
            "longitude": None,
        },
        "cluster": {
            "enabled": False,
            "host": "",
            "port": 7300,
            "login_callsign": "",
            "reconnect_seconds": 30,
        },
        "display": {
            "spot_max_age_minutes": 30,
            "maximum_spots": 500,
            "demo_when_empty": True,
        },
    }

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    for section, values in default.items():
        current = data.get(section)
        if not isinstance(current, dict):
            current = {}
        values.update(current)
        data[section] = values

    return data


class PrefixLookup:
    def __init__(self, path: Path):
        self.items = []
        for entry in json.loads(path.read_text(encoding="utf-8")):
            for prefix in entry["prefixes"]:
                self.items.append((prefix.upper(), entry))
        self.items.sort(key=lambda item: len(item[0]), reverse=True)

    def locate(self, callsign: str):
        callsign = callsign.upper().split("/")[-1]
        for prefix, entry in self.items:
            if callsign.startswith(prefix):
                return (
                    float(entry["lat"]),
                    float(entry["lon"]),
                    entry["name"],
                )
        return None


def band_for(frequency_khz: float) -> str:
    return next(
        (
            name
            for low, high, name in BANDS
            if low <= frequency_khz <= high
        ),
        "other",
    )


def maidenhead(locator: str):
    locator = locator.strip().upper()
    if not re.fullmatch(r"[A-R]{2}[0-9]{2}([A-X]{2})?", locator):
        return None

    longitude = (
        (ord(locator[0]) - 65) * 20
        - 180
        + int(locator[2]) * 2
    )
    latitude = (
        (ord(locator[1]) - 65) * 10
        - 90
        + int(locator[3])
    )

    if len(locator) == 6:
        latitude += (ord(locator[5]) - 65) / 24 + 1 / 48
        longitude += (ord(locator[4]) - 65) / 12 + 1 / 24
    else:
        latitude += 0.5
        longitude += 1.0

    return latitude, longitude


class Store:
    def __init__(self, config: dict, lookup: PrefixLookup):
        self.config = config
        self.lookup = lookup
        self.lock = threading.Lock()
        self.started_at = time.time()
        self.last_update = datetime.now(timezone.utc).isoformat()
        self.last_spot = ""
        self.spots = deque(
            maxlen=config["display"].get("maximum_spots", 500)
        )
        self.cluster_status = (
            "disabled"
            if not config["cluster"].get("enabled")
            else "starting"
        )
        self.last_cluster_line = ""
        self.demo_loaded = False

    def station(self):
        station = self.config["station"]

        if (
            station.get("latitude") is not None
            and station.get("longitude") is not None
        ):
            return (
                float(station["latitude"]),
                float(station["longitude"]),
                station.get("callsign") or "My station",
            )

        location = maidenhead(station.get("locator", ""))
        if location:
            return (
                location[0],
                location[1],
                station.get("callsign")
                or station.get("locator")
                or "My station",
            )

        return None

    def add(
        self,
        reporter: str,
        dx: str,
        frequency,
        comment: str = "",
        timestamp: str | None = None,
    ) -> bool:
        try:
            frequency_khz = float(frequency)
        except (TypeError, ValueError):
            return False

        if frequency_khz < 1000:
            frequency_khz *= 1000

        source = self.lookup.locate(reporter) or self.station()
        target = self.lookup.locate(dx)

        if not source or not target:
            return False

        spot_time = timestamp or datetime.now(timezone.utc).isoformat()
        spot = Spot(
            id=f"{reporter}-{dx}-{time.time_ns()}",
            timestamp=spot_time,
            reporter=reporter.upper(),
            dx=dx.upper(),
            frequency_khz=round(frequency_khz, 3),
            band=band_for(frequency_khz),
            comment=str(comment)[:100],
            source_lat=source[0],
            source_lon=source[1],
            source_name=source[2],
            target_lat=target[0],
            target_lon=target[1],
            target_name=target[2],
        )

        with self.lock:
            self.spots.appendleft(spot)

        self.last_update = datetime.now(timezone.utc).isoformat()
        self.last_spot = f"{spot.reporter} → {spot.dx}"
        return True

    def load_demo(self):
        if self.demo_loaded:
            return

        demo_rows = [
            ("ZL4AAA", "JA1ABC", 14074, "FT8"),
            ("VK3DX", "DL1XYZ", 21074, "FT8"),
            ("K6TEST", "ZL1ABC", 28400, "SSB"),
            ("G4AAA", "PY2DX", 18100, "CW"),
            ("OH2AAA", "VK6DX", 10136, "FT8"),
            ("W1AW", "ZS6ABC", 14200, "SSB"),
            ("JA3AAA", "LU5DX", 7005, "CW"),
            ("ZL2TEST", "VK2ABC", 50110, "6m"),
        ]

        for index, (reporter, dx, frequency, comment) in enumerate(
            demo_rows
        ):
            self.add(
                reporter,
                dx,
                frequency,
                comment,
                datetime.fromtimestamp(
                    time.time() - index * 95,
                    tz=timezone.utc,
                ).isoformat(),
            )

        self.demo_loaded = True

    def payload(self) -> dict:
        cutoff = (
            time.time()
            - self.config["display"].get(
                "spot_max_age_minutes",
                30,
            )
            * 60
        )

        with self.lock:
            items = [
                asdict(spot)
                for spot in self.spots
                if datetime.fromisoformat(spot.timestamp).timestamp()
                >= cutoff
            ]

        if (
            not items
            and self.config["display"].get(
                "demo_when_empty",
                True,
            )
        ):
            self.load_demo()
            with self.lock:
                items = [asdict(spot) for spot in self.spots]

        counts = {}
        for spot in items:
            counts[spot["band"]] = counts.get(spot["band"], 0) + 1

        mode = (
            "live"
            if self.config["cluster"].get("enabled")
            else "demo"
        )

        return {
            "updated": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "cluster_status": self.cluster_status,
            "station": self.config["station"],
            "spots": items,
            "counts": counts,
        }

    def status(self) -> dict:
        return {
            "server": "running",
            "updated": datetime.now(timezone.utc).isoformat(),
            "last_update": self.last_update,
            "uptime_seconds": int(time.time() - self.started_at),
            "cluster_enabled": bool(
                self.config["cluster"].get("enabled")
            ),
            "cluster_status": self.cluster_status,
            "cluster_host": self.config["cluster"].get("host", ""),
            "last_cluster_line": self.last_cluster_line,
            "last_spot": self.last_spot,
            "demo_mode": bool(
                self.config["display"].get(
                    "demo_when_empty",
                    True,
                )
            ),
            "station": self.config["station"],
            "spot_count": len(self.spots),
        }


class Cluster(threading.Thread):
    daemon = True

    def __init__(self, store: Store):
        super().__init__()
        self.store = store

    def run(self):
        cluster = self.store.config["cluster"]

        if not cluster.get("enabled"):
            self.store.cluster_status = "disabled"
            return

        while True:
            try:
                self.store.cluster_status = "connecting"
                with socket.create_connection(
                    (
                        cluster["host"],
                        int(cluster.get("port", 7300)),
                    ),
                    timeout=20,
                ) as connection:
                    login = (
                        cluster.get("login_callsign")
                        or self.store.config["station"].get(
                            "callsign"
                        )
                        or "NOCALL"
                    )
                    connection.sendall((login + "\n").encode())
                    connection.settimeout(60)
                    self.store.cluster_status = "connected"
                    buffer = ""

                    while True:
                        raw = connection.recv(4096)
                        if not raw:
                            raise ConnectionError(
                                "cluster closed the connection"
                            )

                        buffer += raw.decode(errors="ignore")
                        lines = buffer.split("\n")
                        buffer = lines.pop()

                        for line in lines:
                            self.store.last_cluster_line = line[-180:]
                            match = SPOT_RE.search(line)
                            if match:
                                self.store.add(
                                    match.group(1),
                                    match.group(3),
                                    match.group(2),
                                    match.group(4),
                                )
            except Exception as exc:
                self.store.cluster_status = f"error: {exc}"
                time.sleep(
                    int(
                        cluster.get(
                            "reconnect_seconds",
                            30,
                        )
                    )
                )


class LocalHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def server_bind(self):
        TCPServer.server_bind(self)
        self.server_name = str(self.server_address[0])
        self.server_port = int(self.server_address[1])


class Handler(SimpleHTTPRequestHandler):
    store: Store | None = None

    def translate_path(self, path: str) -> str:
        local_path = path.split("?", 1)[0]
        if local_path == "/":
            local_path = "/static/index.html"
        return str(ROOT / local_path.lstrip("/"))

    def json_response(self, data, status: int = 200):
        payload = json.dumps(
            data,
            separators=(",", ":"),
        ).encode()
        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Cache-Control",
            "no-store",
        )
        self.send_header(
            "Content-Length",
            str(len(payload)),
        )
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path.startswith("/api/propagation"):
            return self.json_response(self.store.payload())

        if self.path.startswith("/api/status"):
            return self.json_response(self.store.status())

        return super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/spots":
            return self.json_response(
                {"error": "not found"},
                404,
            )

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )
            body = json.loads(
                self.rfile.read(length) or b"{}"
            )
            rows = body if isinstance(body, list) else [body]
            accepted = 0

            for row in rows:
                accepted += bool(
                    self.store.add(
                        row.get("reporter", ""),
                        row.get("dx", ""),
                        row.get(
                            "frequency_khz",
                            row.get("frequency", ""),
                        ),
                        row.get("comment", ""),
                        row.get("timestamp"),
                    )
                )

            self.json_response({
                "accepted": accepted,
                "received": len(rows),
            })
        except Exception as exc:
            self.json_response(
                {"error": str(exc)},
                400,
            )

    def log_message(self, message, *args):
        print("[HTTP]", message % args)


def main():
    config = load_config()
    store = Store(
        config,
        PrefixLookup(PREFIX_PATH),
    )
    Handler.store = store
    Cluster(store).start()

    host = config["server"].get(
        "host",
        "127.0.0.1",
    )
    port = int(
        config["server"].get(
            "port",
            8765,
        )
    )

    print(
        f"HRPU Propagation: http://{host}:{port}",
        flush=True,
    )

    LocalHTTPServer(
        (host, port),
        Handler,
    ).serve_forever()


if __name__ == "__main__":
    main()
