from __future__ import annotations

from typing import Optional

try:
    import psutil  # optional
except Exception:
    psutil = None


def get_rss_bytes() -> Optional[int]:
    """Process RSS in bytes (best-effort)."""
    if psutil is None:
        return None
    proc = psutil.Process()
    return int(proc.memory_info().rss)


def bytes_to_mb(b: int) -> float:
    return b / (1024.0 * 1024.0)
