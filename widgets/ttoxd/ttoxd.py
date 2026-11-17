#!/usr/bin/env python3
"""ttoxd: demand-driven metrics daemon for TToxThemes widgets, HUD and bar modules.

Run as `python3 -m ttoxd` (from widgets/), `python3 widgets/ttoxd/ttoxd.py` or `widgets/bin/ttoxd`.
Writes $XDG_RUNTIME_DIR/ttox/metrics.json atomically (schema v1, see SCHEMA.md).

Provider plugin API (providers/<name>.py, or ~/.config/ttox/providers/<name>.py):
    NAME = "docker"                 # key in metrics.json
    INTERVAL = 5                    # seconds between collections; 0 = every base poll.
                                    # The effective interval is never shorter than the base poll.
    TIMEOUT = 6                     # optional, seconds (default 4)
    INLINE = False                  # optional; True = cheap, run in the main loop without a thread
    SHAPE = {...}                   # optional; default value of every field, always present in the output
    HISTORY = {"cpu": ("cpu", "total")}   # optional; ring-buffer name -> path of a number in the data
    def available() -> bool         # False -> status "empty"
    def collect(state) -> dict      # state: dict kept between calls; state["config"] = ttoxd.toml section
                                    # raise util.Empty("reason") when the source is missing
"""
from __future__ import annotations

if __name__ == "__main__" and not __package__:  # executed as a script: re-enter through the package
    import os as _os
    import sys as _sys
    _sys.path[0] = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    from ttoxd.ttoxd import main as _main
    _sys.exit(_main())

import argparse
import collections
import importlib.util
import json
import os
import signal
import socket
import sys
import threading
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Set

from . import SCHEMA_VERSION, util

HISTORY_POINTS = 60          # schema v1: ring buffers hold 60 points
DEFAULT_TIMEOUT = 4.0
TTL_SECONDS = 90             # lifetime of ttl-* subscription files
HEARTBEAT = 5.0              # seconds between writes when nothing is subscribed
DEFAULT_POLL = 2.0           # base poll when no colours are installed (the balanced mode value)


class Provider:
    """Wraps one provider module with its schedule and state."""

    def __init__(self, module: Any) -> None:
        self.module = module
        self.name: str = getattr(module, "NAME")
        self.interval: float = float(getattr(module, "INTERVAL", 0))
        self.timeout: float = float(getattr(module, "TIMEOUT", DEFAULT_TIMEOUT))
        self.inline: bool = bool(getattr(module, "INLINE", False))
        self.shape: Dict[str, Any] = dict(getattr(module, "SHAPE", {}))
        self.history: Dict[str, Any] = dict(getattr(module, "HISTORY", {}))
        self.state: Dict[str, Any] = {}
        self.next_due: float = 0.0
        self.entry: Optional[Dict[str, Any]] = None
        self._thread: Optional[threading.Thread] = None
        self._box: Dict[str, Any] = {}
        self._started: float = 0.0
        self._timed_out = False

    # -- result helpers -------------------------------------------------------------------------------
    def make(self, status: str, data: Optional[Dict[str, Any]] = None, reason: str = "",
             message: str = "") -> Dict[str, Any]:
        e: Dict[str, Any] = {"status": status, "ts": round(time.time(), 2), "reason": reason, "message": message}
        for k, v in self.shape.items():
            e[k] = v
        if data:
            for k, v in data.items():
                if k not in ("status", "ts"):
                    e[k] = v
        return e

    def _call(self) -> Dict[str, Any]:
        """Run available()+collect() and turn every outcome into an entry. Never raises."""
        try:
            if not self.module.available():
                return self.make("empty", reason="%s: source not available" % self.name)
            data = self.module.collect(self.state)
            if not isinstance(data, dict):
                return self.make("error", message="%s returned %s, not a dict" % (self.name, type(data).__name__))
            if data.get("status") == "empty":
                return self.make("empty", data, reason=str(data.get("reason", "")))
            return self.make("ok", data)
        except util.Empty as e:
            return self.make("empty", reason=str(e))
        except TimeoutError as e:
            return self.make("error", message=str(e) or "timed out")
        except Exception as e:  # isolation: a broken provider must not take the daemon down
            return self.make("error", message="%s: %s" % (type(e).__name__, e))

    # -- scheduling -----------------------------------------------------------------------------------
    def busy(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, now: float) -> None:
        """Begin a collection. Inline providers finish here; others run in a daemon thread."""
        if self.inline:
            self._box = {"entry": self._call()}
            self._thread = None
            return
        box: Dict[str, Any] = {}
        self._box, self._started, self._timed_out = box, now, False

        def work() -> None:
            box["entry"] = self._call()

        self._thread = threading.Thread(target=work, name="ttoxd-" + self.name, daemon=True)
        self._thread.start()

    def harvest(self, now: float) -> Optional[Dict[str, Any]]:
        """Return a finished entry once, a timeout error once, else None."""
        if "entry" in self._box:
            e = self._box.pop("entry")
            if self._timed_out:      # late result of a call that was already reported as timed out
                self._timed_out = False
                return None
            return e
        if self.busy() and not self._timed_out and now - self._started > self.timeout:
            self._timed_out = True
            return self.make("error", message="%s timed out after %gs" % (self.name, self.timeout))
        return None


def _dig(data: Dict[str, Any], path: Iterable[str]) -> Optional[float]:
    cur: Any = data
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return float(cur) if isinstance(cur, (int, float)) and not isinstance(cur, bool) else None


class Engine:
    """Schedules providers, isolates their failures and builds the schema v1 document."""

    def __init__(self, modules: Iterable[Any], poll: float = DEFAULT_POLL, graphs: bool = True,
                 mode: str = "", config: Optional[Dict[str, Any]] = None,
                 subscriptions: Optional[Callable[[], Set[str]]] = None,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.providers: Dict[str, Provider] = {}
        for m in modules:
            p = Provider(m)
            self.providers[p.name] = p
        self.poll, self.graphs, self.mode = float(poll), bool(graphs), mode
        self.config = config or {}
        self.subscriptions = subscriptions or (lambda: set(self.providers))
        self.clock = clock
        self.wanted: Set[str] = set()
        self.hist: Dict[str, collections.deque] = {}
        for p in self.providers.values():
            p.state["config"] = self.config.get(p.name, {})
            p.state["poll"] = self.poll
            for h in p.history:
                self.hist[h] = collections.deque(maxlen=HISTORY_POINTS)

    def set_mode(self, poll: float, graphs: bool, mode: str) -> None:
        self.poll, self.graphs, self.mode = float(poll), bool(graphs), mode
        for p in self.providers.values():
            p.state["poll"] = self.poll

    def _accept(self, p: Provider, entry: Dict[str, Any]) -> None:
        p.entry = entry
        if entry["status"] == "ok":
            for h, path in p.history.items():
                v = _dig(entry, path)
                if v is not None:
                    self.hist[h].append(round(v, 2))

    def tick(self) -> int:
        """Start due providers and harvest results. Returns the number of entries updated."""
        now = self.clock()
        self.wanted = set(self.subscriptions()) & set(self.providers)
        updated = 0
        for name in sorted(self.providers):
            p = self.providers[name]
            if name in self.wanted and not p.busy() and "entry" not in p._box and now >= p.next_due:
                p.next_due = now + max(p.interval, self.poll)
                p.start(now)
            e = p.harvest(now)
            if e is not None:
                if name in self.wanted:
                    self._accept(p, e)
                    updated += 1
            if name not in self.wanted and p.entry is not None and not p.busy():
                p.entry = None           # demand dropped: forget the stale value
                p.next_due = 0.0
        return updated

    def drain(self, deadline: float = 0.0) -> None:
        """Wait for running providers (used by --once), bounded by each provider's own timeout."""
        end = time.monotonic() + (deadline or max([p.timeout for p in self.providers.values()] + [0.1]) + 0.5)
        while time.monotonic() < end:
            pending = False
            now = self.clock()
            for name, p in self.providers.items():
                e = p.harvest(now)
                if e is not None and name in self.wanted:
                    self._accept(p, e)
                if p.busy() and not p._timed_out:
                    pending = True
            if not pending:
                return
            time.sleep(0.02)

    def document(self) -> Dict[str, Any]:
        provs: Dict[str, Any] = {}
        for name in sorted(self.providers):
            p = self.providers[name]
            if name not in self.wanted:
                provs[name] = p.make("off", reason="not subscribed")
            elif p.entry is None:
                provs[name] = p.make("empty", reason="collecting")
            else:
                provs[name] = p.entry
        hist = {k: list(v) for k, v in sorted(self.hist.items())} if self.graphs else {}
        return {"schema": SCHEMA_VERSION, "ts": round(time.time(), 2), "host": socket.gethostname(),
                "mode": self.mode, "poll": self.poll, "graphs": self.graphs,
                "subscribed": sorted(self.wanted), "providers": provs, "history": hist}

    def write(self, path: str) -> None:
        util.atomic_write(path, json.dumps(self.document(), separators=(",", ":"), sort_keys=True) + "\n")


# ---- provider discovery ---------------------------------------------------------------------------------
def load_modules(extra_dirs: Optional[List[str]] = None) -> List[Any]:
    """Built-in providers plus user plugins from ~/.config/ttox/providers. A broken file is skipped."""
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "providers")
    dirs = [here] + (extra_dirs if extra_dirs is not None else [os.path.join(util.config_dir(), "providers")])
    mods: Dict[str, Any] = {}
    for i, d in enumerate(dirs):
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            try:
                if i == 0:
                    m = importlib.import_module("%s.providers.%s" % (__package__, fn[:-3]))
                else:
                    spec = importlib.util.spec_from_file_location("ttoxd_user_" + fn[:-3], os.path.join(d, fn))
                    m = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(m)  # type: ignore[union-attr]
            except Exception as e:
                print("ttoxd: provider %s not loaded: %s: %s" % (fn, type(e).__name__, e), file=sys.stderr)
                continue
            if hasattr(m, "NAME") and hasattr(m, "collect") and hasattr(m, "available"):
                mods[m.NAME] = m
    return [mods[k] for k in sorted(mods)]


# ---- subscriptions --------------------------------------------------------------------------------------
def subscriptions_dir() -> str:
    d = os.path.join(util.runtime_dir(), "subscriptions")
    os.makedirs(d, exist_ok=True)
    return d


def _names(text: str) -> Set[str]:
    out = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        out.update(x for x in line.replace(",", " ").split() if x)
    return out


def read_subscriptions(sub_dir: Optional[str] = None, persistent: Optional[str] = None,
                       now: Optional[float] = None) -> Set[str]:
    """Union of every client's wish list.

    <runtime>/subscriptions/<client>   one provider name per line (or space/comma separated)
    <runtime>/subscriptions/ttl-<x>    same, but expires TTL_SECONDS after its mtime (used by --metrics-line)
    ~/.config/ttox/subscriptions       persistent list written by `ttox-widgets generate`
    """
    sub_dir = sub_dir or subscriptions_dir()
    persistent = persistent or os.path.join(util.config_dir(), "subscriptions")
    now = time.time() if now is None else now
    wanted: Set[str] = set()
    try:
        entries = list(os.scandir(sub_dir))
    except OSError:
        entries = []
    for ent in entries:
        try:
            if ent.name.startswith("ttl-") and now - ent.stat().st_mtime > TTL_SECONDS:
                os.unlink(ent.path)
                continue
            with open(ent.path, "r") as f:
                wanted |= _names(f.read())
        except OSError:
            continue
    txt = util.read(persistent)
    if txt:
        wanted |= _names(txt)
    return wanted


def subscribe(client: str, names: Iterable[str], ttl: bool = False) -> str:
    path = os.path.join(subscriptions_dir(), ("ttl-" if ttl else "") + client)
    util.atomic_write(path, "\n".join(sorted(set(names))) + "\n")
    return path


def unsubscribe(client: str) -> None:
    for prefix in ("", "ttl-"):
        try:
            os.unlink(os.path.join(subscriptions_dir(), prefix + client))
        except OSError:
            pass


# ---- mode -----------------------------------------------------------------------------------------------
def read_mode() -> Dict[str, Any]:
    """Base poll and graphs flag of the active performance mode (colors.json written by the generator)."""
    c = util.colors()
    mt = c.get("mode_tokens", {}) if isinstance(c, dict) else {}
    return {"mode": c.get("mode", "") if isinstance(c, dict) else "",
            "poll": float(mt.get("poll", DEFAULT_POLL)), "graphs": bool(mt.get("graphs", True))}


# ---- CLI ------------------------------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="ttoxd", description="TToxThemes metrics daemon")
    ap.add_argument("--once", action="store_true", help="collect one round, write the file and exit")
    ap.add_argument("--providers", help="comma list; overrides subscriptions")
    ap.add_argument("--print", dest="print_", action="store_true", help="also print the document (pretty)")
    ap.add_argument("--out", help="output file (default $XDG_RUNTIME_DIR/ttox/metrics.json)")
    ap.add_argument("--poll", type=float, help="base poll in seconds (default: from the active mode)")
    ap.add_argument("--list", action="store_true", help="list providers and exit")
    ap.add_argument("--duration", type=float, default=0, help="stop after N seconds (for measurements)")
    ap.add_argument("--metrics-line", metavar="MODULE", help="print one bar module as text and exit")
    ap.add_argument("--plain", action="store_true", help="with --metrics-line: ASCII labels, no glyphs")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    a = build_parser().parse_args(argv)
    if a.metrics_line:
        from . import line
        return line.main(a.metrics_line, plain=a.plain)
    if os.geteuid() == 0 and os.environ.get("TTOXD_ALLOW_ROOT") != "1":
        print("ttoxd: refusing to run as root. Run it as your user (systemctl --user start ttoxd).\n"
              "       For containers/tests only: TTOXD_ALLOW_ROOT=1.", file=sys.stderr)
        return 1
    modules = load_modules()
    if a.list:
        for m in modules:
            print("%-10s interval=%-5g available=%s" % (m.NAME, getattr(m, "INTERVAL", 0), _safe_available(m)))
        return 0
    mode = read_mode()
    poll = a.poll if a.poll else mode["poll"]
    forced = set(x for x in a.providers.split(",") if x) if a.providers else None
    known = {m.NAME for m in modules}
    if forced and forced - known:
        print("ttoxd: unknown providers: %s" % ", ".join(sorted(forced - known)), file=sys.stderr)
        return 2
    eng = Engine(modules, poll=poll, graphs=mode["graphs"], mode=mode["mode"], config=util.load_config(),
                 subscriptions=(lambda: forced) if forced is not None else read_subscriptions)
    out = a.out or util.metrics_path()

    if a.once:
        eng.tick()
        eng.drain()
        eng.write(out)
        if a.print_:
            print(json.dumps(eng.document(), indent=1, sort_keys=True))
        return 0

    stop = {"flag": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(flag=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(flag=True))
    started = time.monotonic()
    next_tick = started
    last_write = last_mode = 0.0
    current = os.path.join(util.config_dir(), "current")
    target = os.path.realpath(current)
    while not stop["flag"]:
        now = time.monotonic()
        if now - last_mode >= 5.0:              # live mode switch: `current` was repointed
            last_mode = now
            t = os.path.realpath(current)
            if t != target:
                target = t
                mode = read_mode()
                eng.set_mode(a.poll if a.poll else mode["poll"], mode["graphs"], mode["mode"])
        updated = eng.tick()
        if updated or now - last_write >= HEARTBEAT:
            try:
                eng.write(out)
                last_write = now
            except OSError as e:
                print("ttoxd: cannot write %s: %s" % (out, e), file=sys.stderr)
            if a.print_ and updated:
                print(json.dumps(eng.document(), separators=(",", ":"), sort_keys=True), flush=True)
        if a.duration and now - started >= a.duration:
            break
        # Non-inline results arrive between base ticks; wake a little earlier while any are running.
        step = eng.poll if not any(p.busy() for p in eng.providers.values()) else min(eng.poll, 0.25)
        next_tick = max(next_tick + step, now + 0.05) if step == eng.poll else now + step
        time.sleep(max(0.05, next_tick - time.monotonic()))
    return 0


def _safe_available(m: Any) -> str:
    try:
        return "yes" if m.available() else "no"
    except Exception as e:
        return "error (%s)" % e


if __name__ == "__main__":
    sys.exit(main())
