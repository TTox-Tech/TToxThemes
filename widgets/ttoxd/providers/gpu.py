"""GPU busy % best-effort: nvidia-smi, amdgpu gpu_busy_percent, intel via i915 frequency ratio."""
from __future__ import annotations
import glob
import os
from typing import Any, Dict

from .. import util

NAME = "gpu"
INTERVAL = 5
TIMEOUT = 3
SHAPE = {"name": "", "pct": None, "mem_used": None, "mem_total": None, "temp": None, "vendor": ""}


def _drm(pattern: str):
    return sorted(glob.glob("/sys/class/drm/card[0-9]*/" + pattern))


def available() -> bool:
    return util.have("nvidia-smi") or bool(_drm("device/gpu_busy_percent")) or bool(_drm("gt_cur_freq_mhz")) \
        or bool(_drm("device/vendor"))


def collect(state: Dict[str, Any]) -> Dict[str, Any]:
    if util.have("nvidia-smi"):
        rc, out = util.run(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                            "--format=csv,noheader,nounits"], timeout=2.5)
        if rc == 0 and out.strip():
            f = [x.strip() for x in out.splitlines()[0].split(",")]
            num = lambda s: float(s) if s.replace(".", "", 1).isdigit() else None  # noqa: E731
            return {"vendor": "nvidia", "name": f[0], "pct": num(f[1]), "mem_used": num(f[2]),
                    "mem_total": num(f[3]), "temp": num(f[4])}
    for p in _drm("device/gpu_busy_percent"):
        return {"vendor": "amd", "name": os.path.basename(os.path.dirname(os.path.dirname(p))),
                "pct": float(util.read_int(p) or 0)}
    for p in _drm("gt_cur_freq_mhz"):
        d = os.path.dirname(p)
        cur, mx = util.read_int(p), util.read_int(os.path.join(d, "gt_max_freq_mhz"))
        # frequency ratio is a rough load proxy; exact busy % needs intel_gpu_top (root) — documented in SCHEMA
        return {"vendor": "intel", "name": "intel " + os.path.basename(d),
                "pct": round(100.0 * cur / mx, 1) if cur is not None and mx else None}
    raise util.Empty("no supported GPU telemetry (nvidia-smi, amdgpu, i915)")
