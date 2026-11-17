"""Temperatures and fans from /sys/class/hwmon (and thermal_zone as a fallback)."""
from __future__ import annotations
import glob
import os
from typing import Any, Dict

from .. import util

NAME = "sensors"
INTERVAL = 5
INLINE = True
SHAPE = {"cpu_temp": None, "temps": [], "fans": []}
HISTORY = {"temp": ("cpu_temp",)}
CPU_CHIPS = ("coretemp", "k10temp", "zenpower", "cpu_thermal", "acpitz")


def available() -> bool:
    return bool(glob.glob("/sys/class/hwmon/hwmon*") or glob.glob("/sys/class/thermal/thermal_zone*"))


def collect(state: Dict[str, Any]) -> Dict[str, Any]:
    temps, fans, cpu = [], [], None
    for hw in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
        chip = (util.read(os.path.join(hw, "name")) or "?").strip()
        for t in sorted(glob.glob(os.path.join(hw, "temp*_input"))):
            v = util.read_int(t)
            if v is None:
                continue
            label = (util.read(t.replace("_input", "_label")) or chip).strip()
            c = round(v / 1000.0, 1)
            temps.append({"chip": chip, "label": label, "c": c})
            if cpu is None and chip in CPU_CHIPS:
                cpu = c
        for fpath in sorted(glob.glob(os.path.join(hw, "fan*_input"))):
            v = util.read_int(fpath)
            if v is not None:
                fans.append({"chip": chip, "label": os.path.basename(fpath)[:-6], "rpm": v})
    if not temps:
        for z in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
            v = util.read_int(os.path.join(z, "temp"))
            if v is not None:
                kind = (util.read(os.path.join(z, "type")) or "zone").strip()
                temps.append({"chip": kind, "label": kind, "c": round(v / 1000.0, 1)})
    if cpu is None and temps:
        cpu = max(t["c"] for t in temps)
    if not temps and not fans:
        raise util.Empty("no temperature or fan sensors exposed")
    return {"cpu_temp": cpu, "temps": temps[:16], "fans": fans[:8]}
