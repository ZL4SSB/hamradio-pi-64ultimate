"""JSON configuration services for HamRadio-Pi Ultimate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigService:
    """Load and save JSON configuration files safely."""

    @staticmethod
    def load_json(
        path: Path,
        default: dict[str, Any],
    ) -> dict[str, Any]:
        """Load JSON data or return a copy of the supplied default."""

        if not path.exists():
            return dict(default)

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return dict(default)

        if not isinstance(data, dict):
            return dict(default)

        return data

    @staticmethod
    def save_json(
        path: Path,
        data: dict[str, Any],
    ) -> None:
        """Write JSON data using an atomic temporary file."""

        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_suffix(path.suffix + ".tmp")

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            file.write("\n")

        temporary_path.replace(path)
