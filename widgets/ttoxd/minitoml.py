"""TOML reading (tomllib when available, else a small subset parser) and a small writer.

The fallback parser covers what TToxThemes files use: comments, [table], [a.b], [[array-of-tables]],
key = "string" | 'string' | int | float | true/false | [array, possibly over several lines].
It does not cover inline tables, dates, multi-line strings or dotted keys.
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, List

try:  # Python >= 3.11
    import tomllib as _tomllib
except ImportError:  # pragma: no cover - exercised explicitly through loads_fallback in tests
    _tomllib = None


class TomlError(ValueError):
    pass


def _strip_comment(line: str) -> str:
    out, quote = [], ""
    i = 0
    while i < len(line):
        c = line[i]
        if quote:
            out.append(c)
            if c == "\\" and quote == '"' and i + 1 < len(line):
                out.append(line[i + 1]); i += 1
            elif c == quote:
                quote = ""
        elif c in "\"'":
            quote = c; out.append(c)
        elif c == "#":
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).strip()


def _split_array(body: str) -> List[str]:
    parts, cur, depth, quote = [], [], 0, ""
    i = 0
    while i < len(body):
        c = body[i]
        if quote:
            cur.append(c)
            if c == "\\" and quote == '"' and i + 1 < len(body):
                cur.append(body[i + 1]); i += 1
            elif c == quote:
                quote = ""
        elif c in "\"'":
            quote = c; cur.append(c)
        elif c == "[":
            depth += 1; cur.append(c)
        elif c == "]":
            depth -= 1; cur.append(c)
        elif c == "," and depth == 0:
            parts.append("".join(cur).strip()); cur = []
        else:
            cur.append(c)
        i += 1
    last = "".join(cur).strip()
    if last:
        parts.append(last)
    return parts


def _value(s: str) -> Any:
    s = s.strip()
    if not s:
        raise TomlError("empty value")
    if s[0] == '"':
        if len(s) < 2 or s[-1] != '"':
            raise TomlError("unterminated string: " + s)
        try:
            return json.loads(s)
        except ValueError as e:
            raise TomlError(str(e))
    if s[0] == "'":
        if len(s) < 2 or s[-1] != "'":
            raise TomlError("unterminated string: " + s)
        return s[1:-1]
    if s[0] == "[":
        if s[-1] != "]":
            raise TomlError("unterminated array: " + s)
        return [_value(x) for x in _split_array(s[1:-1])]
    if s == "true":
        return True
    if s == "false":
        return False
    try:
        return int(s.replace("_", ""))
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        raise TomlError("unsupported value: " + s)


def _bracket_balance(s: str) -> int:
    n, quote = 0, ""
    for c in s:
        if quote:
            if c == quote:
                quote = ""
        elif c in "\"'":
            quote = c
        elif c == "[":
            n += 1
        elif c == "]":
            n -= 1
    return n


def loads_fallback(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    cur = root
    pending = ""
    for raw in text.splitlines():
        line = _strip_comment(raw)
        if pending:
            line = pending + " " + line
            pending = ""
        if not line:
            continue
        m = re.match(r"^\[\[([A-Za-z0-9_.\-]+)\]\]$", line)
        if m:
            node = root
            keys = m.group(1).split(".")
            for k in keys[:-1]:
                node = node.setdefault(k, {})
            lst = node.setdefault(keys[-1], [])
            if not isinstance(lst, list):
                raise TomlError("not an array of tables: " + m.group(1))
            cur = {}
            lst.append(cur)
            continue
        m = re.match(r"^\[([A-Za-z0-9_.\-]+)\]$", line)
        if m:
            cur = root
            for k in m.group(1).split("."):
                cur = cur.setdefault(k, {})
                if isinstance(cur, list):
                    cur = cur[-1]
            continue
        if "=" not in line:
            raise TomlError("cannot parse line: " + raw)
        key, val = line.split("=", 1)
        key = key.strip().strip('"')
        if _bracket_balance(val) > 0:  # array continues on following lines
            pending = line
            continue
        cur[key] = _value(val)
    if pending:
        raise TomlError("unterminated array at end of file")
    return root


def loads(text: str) -> Dict[str, Any]:
    if _tomllib is not None:
        try:
            return _tomllib.loads(text)
        except _tomllib.TOMLDecodeError as e:
            raise TomlError(str(e))
    return loads_fallback(text)


def load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return loads(f.read())


def _dump_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_dump_value(x) for x in v) + "]"
    raise TomlError("cannot write value of type %s" % type(v).__name__)


def dumps(data: Dict[str, Any]) -> str:
    """Write scalars first, then tables, then arrays of tables. Key order is preserved (callers sort)."""
    out: List[str] = []
    for k, v in data.items():
        if not isinstance(v, dict) and not (isinstance(v, list) and v and isinstance(v[0], dict)):
            out.append("%s = %s" % (k, _dump_value(v)))
    for k, v in data.items():
        if isinstance(v, dict):
            out.append("")
            out.append("[%s]" % k)
            for kk, vv in v.items():
                out.append("%s = %s" % (kk, _dump_value(vv)))
    for k, v in data.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            for item in v:
                out.append("")
                out.append("[[%s]]" % k)
                for kk, vv in item.items():
                    out.append("%s = %s" % (kk, _dump_value(vv)))
    return "\n".join(out).strip() + "\n"
