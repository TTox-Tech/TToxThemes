"""cpu total/per-core, load, uptime, ram, swap, disks, io. psutil when importable (and not disabled with
TTOXD_NO_PSUTIL=1), else /proc parsing. Both paths produce the same fields."""
from __future__ import annotations
import os
import time
from typing import Any, Dict, List, Tuple

from .. import util

NAME = "system"
INTERVAL = 0          # every base poll
INLINE = True         # a few /proc reads: cheaper than a thread
SHAPE = {"cpu": {"total": 0.0, "cores": []}, "load": [0.0, 0.0, 0.0], "uptime": 0, "uptime_h": "",
         "ram": {"used": 0, "total": 0, "pct": 0.0}, "swap": {"used": 0, "total": 0, "pct": 0.0},
         "disks": [], "io": {"read_bps": 0.0, "write_bps": 0.0}, "backend": ""}
HISTORY = {"cpu": ("cpu", "total"), "ram": ("ram", "pct")}

SKIP_FS = {"proc", "sysfs", "devtmpfs", "devpts", "tmpfs", "cgroup", "cgroup2", "overlay", "squashfs",
           "securityfs", "pstore", "debugfs", "tracefs", "mqueue", "hugetlbfs", "fusectl", "configfs",
           "autofs", "binfmt_misc", "nsfs", "bpf", "efivarfs", "ramfs", "rpc_pipefs", "fuse.portal"}

try:
    if os.environ.get("TTOXD_NO_PSUTIL") == "1":
        raise ImportError("disabled")
    import psutil  # type: ignore
except ImportError:
    psutil = None


def available() -> bool:
    return os.path.exists("/proc/stat") or psutil is not None


def _proc_cpu() -> List[Tuple[int, int]]:
    """[(busy, total)] for 'cpu' then each core, from /proc/stat."""
    out = []
    for line in (util.read("/proc/stat") or "").splitlines():
        if not line.startswith("cpu"):
            break
        f = [int(x) for x in line.split()[1:]]
        idle = f[3] + (f[4] if len(f) > 4 else 0)
        total = sum(f[:8])                     # guest time is already part of user/nice
        out.append((total - idle, total))
    return out


def _cpu(state: Dict[str, Any]) -> Dict[str, Any]:
    cur = _proc_cpu()
    prev = state.get("cpu_prev")
    state["cpu_prev"] = cur
    if not prev or len(prev) != len(cur):
        return {"total": 0.0, "cores": [0.0] * max(0, len(cur) - 1)}
    vals = []
    for (b0, t0), (b1, t1) in zip(prev, cur):
        dt = t1 - t0
        vals.append(round(100.0 * (b1 - b0) / dt, 1) if dt > 0 else 0.0)
    return {"total": vals[0], "cores": vals[1:]}


def _meminfo() -> Dict[str, int]:
    m = {}
    for line in (util.read("/proc/meminfo") or "").splitlines():
        k, _, v = line.partition(":")
        try:
            m[k] = int(v.split()[0]) * 1024
        except (ValueError, IndexError):
            pass
    return m


def _disks(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    # statvfs is cheap but mounts rarely change: refresh the mount list every 30 s
    now = time.monotonic()
    if now - state.get("mounts_at", -1e9) > 30:
        mounts, seen = [], set()
        for line in (util.read("/proc/mounts") or "").splitlines():
            f = line.split()
            if len(f) < 3 or f[2] in SKIP_FS or f[0] in seen or f[1].startswith(("/snap", "/proc", "/sys", "/run")):
                continue
            seen.add(f[0])
            mounts.append(f[1].replace("\\040", " "))
        cfg = state.get("config") or {}
        want = cfg.get("mounts")
        state["mounts"] = [m for m in mounts if not want or m in want][:6] or ["/"]
        state["mounts_at"] = now
    out = []
    for mnt in state["mounts"]:
        try:
            st = os.statvfs(mnt)
        except OSError:
            continue
        total = st.f_blocks * st.f_frsize
        used = total - st.f_bfree * st.f_frsize
        if total:
            out.append({"mount": mnt, "used": used, "total": total, "pct": util.pct(used, total)})
    return out


def _io(state: Dict[str, Any]) -> Dict[str, float]:
    rd = wr = 0
    for line in (util.read("/proc/diskstats") or "").splitlines():
        f = line.split()
        if len(f) < 10:
            continue
        name = f[2]
        # whole disks only (partitions are not in /sys/block); skip virtual devices
        if name.startswith(("loop", "ram", "zram", "sr", "dm-", "md")) or not os.path.isdir("/sys/block/" + name):
            continue
        rd += int(f[5]) * 512
        wr += int(f[9]) * 512
    now = time.monotonic()
    prev = state.get("io_prev")
    state["io_prev"] = (now, rd, wr)
    if not prev or now <= prev[0]:
        return {"read_bps": 0.0, "write_bps": 0.0}
    dt = now - prev[0]
    return {"read_bps": round(max(0, rd - prev[1]) / dt, 1), "write_bps": round(max(0, wr - prev[2]) / dt, 1)}


def collect(state: Dict[str, Any]) -> Dict[str, Any]:
    if psutil is not None:
        cores = psutil.cpu_percent(percpu=True)
        cpu = {"total": round(sum(cores) / len(cores), 1) if cores else 0.0, "cores": [round(c, 1) for c in cores]}
        vm, sw = psutil.virtual_memory(), psutil.swap_memory()
        ram = {"used": int(vm.total - vm.available), "total": int(vm.total)}
        swap = {"used": int(sw.used), "total": int(sw.total)}
        backend = "psutil"
    else:
        cpu = _cpu(state)
        m = _meminfo()
        total = m.get("MemTotal", 0)
        ram = {"used": total - m.get("MemAvailable", m.get("MemFree", 0)), "total": total}
        swap = {"used": m.get("SwapTotal", 0) - m.get("SwapFree", 0), "total": m.get("SwapTotal", 0)}
        backend = "proc"
    ram["pct"] = util.pct(ram["used"], ram["total"])
    swap["pct"] = util.pct(swap["used"], swap["total"])
    try:
        load = [round(x, 2) for x in os.getloadavg()]
    except OSError:
        load = [0.0, 0.0, 0.0]
    up = float((util.read("/proc/uptime") or "0").split()[0])
    return {"cpu": cpu, "load": load, "uptime": int(up), "uptime_h": util.human_uptime(up),
            "ram": ram, "swap": swap, "disks": _disks(state), "io": _io(state), "backend": backend}
