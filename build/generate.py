#!/usr/bin/env python3
"""TToxThemes generator. Discovers build/targets/*.py and writes dist/.

Target module contract:
    NAME = "kde_colorscheme"          # unique
    PACK = "kde"                      # core | kde | xfce | widgets | apps | boot | kali
    ONCE = False                      # optional; True = render called once (ctx of first palette, use ctx.all_palettes)
    def render(ctx) -> dict[str, str | bytes]   # keys: paths relative to dist/ ; must be a pure function of ctx

Usage: generate.py [--only NAME[,NAME]] [--out DIR] [--check] [--list]
  --check  render twice and fail if outputs differ (determinism), write nothing.
"""
from __future__ import annotations
import argparse, importlib.util, os, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "build"))
from palettes import PALETTES   # noqa: E402
from tokens import TOKENS, MODES  # noqa: E402
import lib  # noqa: E402

REQUIRED = ["title", "bg", "surface", "raised", "line", "muted", "fg", "fg_hi", "accent", "accent2",
            "accent_text", "folder", "ok", "warn", "err", "cursor", "term"]

def validate():
    for name, p in PALETTES.items():
        missing = [k for k in REQUIRED if k not in p]
        if missing: sys.exit(f"palette {name}: missing {missing}")
        if len(p["term"]) != 16: sys.exit(f"palette {name}: term needs 16 colours")

def load_targets(only=None):
    tdir = os.path.join(ROOT, "build", "targets")
    mods = []
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".py") or fn.startswith("_"): continue
        spec = importlib.util.spec_from_file_location("targets." + fn[:-3], os.path.join(tdir, fn))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        if not hasattr(m, "render"): continue
        m.NAME = getattr(m, "NAME", fn[:-3]); m.PACK = getattr(m, "PACK", "core")
        if only and m.NAME not in only: continue
        mods.append(m)
    return mods

def render_all(mods):
    out, owners, errors = {}, {}, []
    for m in mods:
        names = list(PALETTES)[:1] if getattr(m, "ONCE", False) else list(PALETTES)
        for name in names:
            ctx = lib.Ctx(name=name, p=PALETTES[name], tokens=TOKENS, modes=MODES, all_palettes=PALETTES, root=ROOT)
            try:
                files = m.render(ctx) or {}
            except Exception as e:  # one broken target must not hide the others
                errors.append(f"{m.NAME}[{name}]: {type(e).__name__}: {e}"); continue
            for path, data in files.items():
                path = os.path.normpath(path)
                if path.startswith("..") or os.path.isabs(path):
                    errors.append(f"{m.NAME}: illegal path {path}"); continue
                if path in out and out[path] != data:
                    errors.append(f"{m.NAME}: path {path} already written by {owners[path]} with different content"); continue
                out[path] = data; owners[path] = m.NAME
    return out, owners, errors

def digest(out):
    h = hashlib.sha256()
    for k in sorted(out):
        v = out[k]; h.update(k.encode()); h.update(v if isinstance(v, bytes) else v.encode())
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only"); ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    ap.add_argument("--check", action="store_true"); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    validate()
    mods = load_targets(set(a.only.split(",")) if a.only else None)
    if a.list:
        for m in mods: print(f"{m.PACK:8} {m.NAME}")
        return 0
    out, owners, errors = render_all(mods)
    if a.check:
        out2, _, _ = render_all(mods)
        if digest(out) != digest(out2): errors.append("non-deterministic output")
    else:
        for path, data in out.items():
            full = os.path.join(a.out, path); os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb" if isinstance(data, bytes) else "w") as f: f.write(data)
            if path.endswith(".sh") or "/bin/" in path: os.chmod(full, 0o755)
    per = {}
    for path, o in owners.items(): per[o] = per.get(o, 0) + 1
    for m in mods: print(f"  {m.PACK:8} {m.NAME:28} {per.get(m.NAME, 0):4} files")
    print(f"{len(out)} files, digest {digest(out)[:12]}" + ("" if not a.check else " (check only)"))
    for e in errors: print("ERROR " + e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
