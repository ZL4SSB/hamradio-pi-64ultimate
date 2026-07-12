from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ApplicationEntry:
    name: str
    category: str
    command: str
    package: str
    description: str
    recommended: bool = False


def load_catalogue(path: Path) -> list[ApplicationEntry]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [ApplicationEntry(**item) for item in raw]


def is_installed(entry: ApplicationEntry) -> bool:
    return shutil.which(entry.command) is not None
