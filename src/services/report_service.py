from __future__ import annotations
import platform
import subprocess
from datetime import datetime
from constants import APP_NAME, APP_VERSION, REPORTS_DIR
from services.system_service import system_snapshot
from services.hardware_service import scan_hardware

def _command(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=12)
        return (result.stdout + result.stderr).strip()
    except Exception as exc:
        return f"Unavailable: {exc}"

def generate_system_report() -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = REPORTS_DIR / f"hamradio-pi-report-{stamp}.txt"
    snapshot = system_snapshot()
    hardware = scan_hardware()

    lines = [
        f"{APP_NAME} {APP_VERSION}",
        "System Report",
        "=" * 72,
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Python: {platform.python_version()}",
        "",
        "SYSTEM",
        "-" * 72,
    ]
    for key, value in snapshot.items():
        lines.append(f"{key}: {value[0]} | {value[1]}")

    lines.extend(["", "HARDWARE", "-" * 72])
    for item in hardware:
        lines.extend([
            f"{item.name} [{item.kind}]",
            f"  {item.detail}",
            f"  Recommendation: {item.recommendation}",
        ])

    lines.extend([
        "",
        "BLOCK DEVICES",
        "-" * 72,
        _command(["lsblk", "-o", "NAME,PATH,SIZE,FSTYPE,TYPE,TRAN,RM,MOUNTPOINTS,MODEL"]),
        "",
        "USB DEVICES",
        "-" * 72,
        _command(["lsusb"]),
        "",
        "NETWORK",
        "-" * 72,
        _command(["ip", "address"]),
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)
