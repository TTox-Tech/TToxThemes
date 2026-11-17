"""Battery from /sys/class/power_supply (no upower dependency)."""
from __future__ import annotations
import glob
import os
from typing import Any, Dict, List

from .. import util

NAME = "battery"
INTERVAL = 15
INLINE = True
SHAPE = {"present": False, "pct": None, "state": "", "watts": None, "health": None, "ac": None}


def _bats() -> List[str]:
    return [p for p in sorted(glob.glob("/sys/class/power_supply/*"))
            if (util.read(os.path.join(p, "type")) or "").strip() == "Battery"
            and (util.read(os.path.join(p, "scope")) or "System").strip() != "Device"]


def available() -> bool:
    return bool(_bats())


def collect(state: Dict[str, Any]) -> Dict[str, Any]:
    bats = _bats()
    if not bats:
        raise util.Empty("no battery")
    b = bats[0]
    r = lambda k: util.read_int(os.path.join(b, k))  # noqa: E731
    pct = r("capacity")
    st = (util.read(os.path.join(b, "status")) or "").strip()
    watts = None
    if r("power_now") is not None:
        watts = round(r("power_now") / 1e6, 1)
    elif r("current_now") is not None and r("voltage_now") is not None:
        watts = round(r("current_now") * r("voltage_now") / 1e12, 1)
    full, design = r("energy_full") or r("charge_full"), r("energy_full_design") or r("charge_full_design")
    health = util.pct(full, design) if full and design else None
    ac = None
    for p in glob.glob("/sys/class/power_supply/*"):
        if (util.read(os.path.join(p, "type")) or "").strip() == "Mains":
            ac = util.read_int(os.path.join(p, "online")) == 1
    return {"present": True, "pct": pct, "state": st.lower(), "watts": watts, "health": health, "ac": ac}
