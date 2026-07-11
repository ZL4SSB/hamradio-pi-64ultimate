"""JSON configuration services."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigService:
    """Load and save JSON configuration files safely."""

    @staticmethod
    def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return dict(default)

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return dict(default)

        return data if isinstance(data, dict) else dict(default)

    @staticmethod
    def save_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")

        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            file.write("\n")

        temporary.replace(path)
