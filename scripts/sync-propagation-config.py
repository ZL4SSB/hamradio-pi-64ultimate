#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "config" / "settings.json"
CONFIG_PATH = ROOT / "propagation" / "config.json"


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> int:
    settings = load_json(SETTINGS_PATH, {})
    config = load_json(CONFIG_PATH, {})

    config.setdefault(
        "server",
        {
            "host": "127.0.0.1",
            "port": 8765,
        },
    )
    config["server"].update({
        "host": "127.0.0.1",
        "port": 8765,
    })

    config["station"] = {
        "callsign": str(
            settings.get("callsign", "")
        ).strip().upper(),
        "locator": str(
            settings.get("locator", "")
        ).strip().upper(),
        "latitude": None,
        "longitude": None,
    }

    try:
        cluster_port = int(
            settings.get(
                "dx_cluster_port",
                7300,
            )
        )
    except (TypeError, ValueError):
        cluster_port = 7300

    cluster_host = str(
        settings.get(
            "dx_cluster_host",
            "",
        )
    ).strip()

    cluster_login = str(
        settings.get(
            "dx_cluster_login",
            "",
        )
    ).strip().upper()

    config["cluster"] = {
        "enabled": bool(
            settings.get(
                "dx_cluster_enabled",
                False,
            )
            and cluster_host
        ),
        "host": cluster_host,
        "port": cluster_port,
        "login_callsign": (
            cluster_login
            or config["station"]["callsign"]
        ),
        "reconnect_seconds": 30,
    }

    config["display"] = {
        "spot_max_age_minutes": 30,
        "maximum_spots": 500,
        "demo_when_empty": bool(
            settings.get(
                "propagation_demo_mode",
                True,
            )
        ),
    }

    CONFIG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
