#!/usr/bin/env python3

import json
from pathlib import Path

CATALOGUE_FILE = Path(__file__).resolve().parent / "data" / "applications.json"


def load_applications() -> list[dict]:
    try:
        data = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    applications = data.get("applications", [])
    return applications if isinstance(applications, list) else []
