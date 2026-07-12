from __future__ import annotations
import tkinter as tk
from constants import ASSETS_DIR

_CACHE: dict[tuple[str, int, int], tk.PhotoImage] = {}

def load_image(filename: str, width: int, height: int) -> tk.PhotoImage | None:
    key = (filename, width, height)
    if key in _CACHE:
        return _CACHE[key]
    path = ASSETS_DIR / "branding" / filename
    if not path.exists():
        return None
    try:
        image = tk.PhotoImage(file=str(path))
        if image.width() > width or image.height() > height:
            sx = max(1, image.width() // width)
            sy = max(1, image.height() // height)
            image = image.subsample(sx, sy)
        _CACHE[key] = image
        return image
    except tk.TclError:
        return None
