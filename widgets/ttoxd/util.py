"""Helpers shared by ttoxd providers and the widget tools. Standard library only."""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Sequence, Tuple

SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9@_.:\-]{0,62}$")
SAFE_IFACE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,14}$")


class Empty(Exception):
    """Raised by a provider when its data source is missing: becomes status "empty"."""


def config_dir() -> str:
    return os.environ.get("TTOX_CONFIG") or os.path.join(
        os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"), "ttox")


def cache_dir() -> str:
    return os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "ttox")


def runtime_dir() -> str:
    """$XDG_RUNTIME_DIR/ttox; without XDG_RUNTIME_DIR a private per-user dir under the temp dir."""
    base = os.environ.get("XDG_RUNTIME_DIR")
    if not base:
        base = os.path.join(tempfile.gettempdir(), "ttox-runtime-%d" % os.getuid())
    d = os.path.join(base, "ttox")
    os.makedirs(d, mode=0o700, exist_ok=True)
    return d


def metrics_path() -> str:
    return os.path.join(runtime_dir(), "metrics.json")


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: Sequence[str], timeout: float = 3.0) -> Tuple[int, str]:
    """Run a command without a shell. Returns (returncode, stdout). Raises Empty when it is not installed,
    TimeoutError when it runs too long."""
    try:
        r = subprocess.run(list(cmd), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           stdin=subprocess.DEVNULL, timeout=timeout, universal_newlines=True,
                           errors="replace", env=dict(os.environ, LC_ALL="C"))
    except FileNotFoundError:
        raise Empty("%s is not installed" % cmd[0])
    except subprocess.TimeoutExpired:
        raise TimeoutError("%s timed out after %gs" % (cmd[0], timeout))
    return r.returncode, r.stdout


def read(path: str, default: Optional[str] = None) -> Optional[str]:
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()
    except OSError:
        return default


def read_int(path: str, default: Optional[int] = None) -> Optional[int]:
    s = read(path)
    try:
        return int(s.strip()) if s is not None else default
    except ValueError:
        return default


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=d)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_json(path: str, default: Any = None) -> Any:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def human_bytes(n: float, digits: int = 1) -> str:
    """1536 -> '1.5K' (binary units, one letter)."""
    n = float(n)
    for unit in ("B", "K", "M", "G", "T"):
        if abs(n) < 1024 or unit == "T":
            if unit == "B":
                return "%dB" % n
            return "%.*f%s" % (digits, n, unit)
        n /= 1024.0
    return "%.*fT" % (digits, n)


def human_rate(bps: float) -> str:
    """Bytes per second -> '1.20 MB/s'."""
    if bps >= 1024 * 1024:
        return "%.2f MB/s" % (bps / 1048576.0)
    if bps >= 1024:
        return "%.0f KB/s" % (bps / 1024.0)
    return "%.0f B/s" % bps


def short_rate(bps: float) -> str:
    """Bytes per second -> '1.2M' for the bar."""
    if bps >= 1048576:
        return "%.1fM" % (bps / 1048576.0)
    if bps >= 1024:
        return "%.0fK" % (bps / 1024.0)
    return "0K"


def human_uptime(seconds: float) -> str:
    s = int(seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m = s // 60
    if d:
        return "%d d %d h" % (d, h)
    return "%d h %02d m" % (h, m)


def pct(part: float, whole: float) -> float:
    return round(100.0 * part / whole, 1) if whole else 0.0


def listening_ports() -> List[int]:
    """TCP ports in LISTEN state from /proc/net/tcp{,6}. Cheap; no process names."""
    ports = set()
    for p in ("/proc/net/tcp", "/proc/net/tcp6"):
        txt = read(p)
        if not txt:
            continue
        for line in txt.splitlines()[1:]:
            f = line.split()
            if len(f) > 3 and f[3] == "0A":
                try:
                    ports.add(int(f[1].rsplit(":", 1)[1], 16))
                except (ValueError, IndexError):
                    pass
    return sorted(ports)


def colors() -> Dict[str, Any]:
    """Active runtime colours/tokens (~/.config/ttox/current/colors.json) or {}."""
    return load_json(os.path.join(config_dir(), "current", "colors.json"), {}) or {}


def load_config() -> Dict[str, Any]:
    """~/.config/ttox/ttoxd.toml (optional)."""
    from . import minitoml
    path = os.path.join(config_dir(), "ttoxd.toml")
    if not os.path.exists(path):
        return {}
    try:
        return minitoml.load(path)
    except (OSError, ValueError):
        return {}
