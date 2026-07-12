from __future__ import annotations
import subprocess
from constants import BASE_DIR

def git_status() -> dict:
    if not (BASE_DIR / ".git").exists():
        return {"ok": False, "message": "This folder is not a Git working copy."}
    try:
        subprocess.run(
            ["git", "-C", str(BASE_DIR), "fetch", "--quiet"],
            check=True, timeout=45
        )
        branch = subprocess.run(
            ["git", "-C", str(BASE_DIR), "branch", "--show-current"],
            capture_output=True, text=True, timeout=10
        ).stdout.strip() or "unknown"
        counts = subprocess.run(
            ["git", "-C", str(BASE_DIR), "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
            capture_output=True, text=True, timeout=10
        )
        if counts.returncode:
            return {"ok": False, "message": counts.stderr.strip() or "No upstream branch configured."}
        ahead, behind = counts.stdout.strip().split()
        dirty = subprocess.run(
            ["git", "-C", str(BASE_DIR), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10
        ).stdout.strip()
        return {
            "ok": True,
            "branch": branch,
            "ahead": int(ahead),
            "behind": int(behind),
            "dirty": bool(dirty),
            "message": "Up to date" if behind == "0" else f"{behind} update(s) available",
        }
    except Exception as exc:
        return {"ok": False, "message": f"Update check failed: {exc}"}
