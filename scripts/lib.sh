#!/usr/bin/env bash
# TToxThemes shared shell helpers. Source this; do not execute.
# Env: TTOX_HOME (installed kit root, default ~/.local/share/ttox), TTOX_CONFIG (~/.config/ttox),
#      TTOX_DRY_RUN=1 (print instead of change), TTOX_YES=1 (no prompts).
: "${TTOX_HOME:=${XDG_DATA_HOME:-$HOME/.local/share}/ttox}"
: "${TTOX_CONFIG:=${XDG_CONFIG_HOME:-$HOME/.config}/ttox}"
: "${TTOX_DRY_RUN:=0}"; : "${TTOX_YES:=0}"
TTOX_DIST="$TTOX_HOME/dist"
TTOX_STATE="$TTOX_CONFIG/state.toml"
TTOX_BACKUP_ROOT="$TTOX_CONFIG/backup"

_c() { [ -t 2 ] && printf '\033[%sm' "$1" >&2 || true; }
log()  { _c '0;37'; printf '  %s\n' "$*" >&2; _c 0; }
ok()   { _c '0;32'; printf '  ok   %s\n' "$*" >&2; _c 0; }
warn() { _c '0;33'; printf '  warn %s\n' "$*" >&2; _c 0; }
err()  { _c '0;31'; printf '  FAIL %s\n' "$*" >&2; _c 0; }
step() { _c '1;37'; printf '\n== %s\n' "$*" >&2; _c 0; }
have() { command -v "$1" >/dev/null 2>&1; }

# run CMD...: execute, or print when dry-run.
run() { if [ "$TTOX_DRY_RUN" = 1 ]; then printf '  [dry-run] %s\n' "$*" >&2; else "$@"; fi; }

confirm() { # confirm "question" -> 0 yes
  [ "$TTOX_YES" = 1 ] && return 0
  [ "$TTOX_DRY_RUN" = 1 ] && return 0
  local a; printf '  %s [y/N] ' "$1" >&2; read -r a || return 1; case "$a" in y|Y|yes) return 0;; *) return 1;; esac
}

# Backups: one snapshot dir per apply; manifest lists "path<TAB>existed(0/1)".
ttox_snapshot_begin() { # sets TTOX_SNAP
  TTOX_SNAP="${TTOX_SNAP:-$TTOX_BACKUP_ROOT/$(date +%Y%m%d-%H%M%S)-$$}"
  [ "$TTOX_DRY_RUN" = 1 ] || mkdir -p "$TTOX_SNAP/files"
  export TTOX_SNAP
}
backup() { # backup <abs path>: record original once per snapshot
  local f="$1"; [ -n "${TTOX_SNAP:-}" ] || ttox_snapshot_begin
  [ "$TTOX_DRY_RUN" = 1 ] && return 0
  local man="$TTOX_SNAP/manifest.tsv"
  if [ -f "$man" ] && cut -f1 "$man" | grep -Fxq -- "$f"; then return 0; fi
  if [ -e "$f" ] || [ -L "$f" ]; then
    mkdir -p "$TTOX_SNAP/files$(dirname "$f")"; cp -a "$f" "$TTOX_SNAP/files$f"; printf '%s\t1\n' "$f" >>"$man"
  else printf '%s\t0\n' "$f" >>"$man"; fi
}
# install_file SRC DST: backup DST then copy (creates dirs).
install_file() { local s="$1" d="$2"; backup "$d"; run mkdir -p "$(dirname "$d")"; run cp -f "$s" "$d"; }
# install_dir SRC DST: backup DST (as a whole) then replace it with a copy of SRC.
install_dir() { local s="$1" d="$2"; backup "$d"; run mkdir -p "$(dirname "$d")"; run rm -rf "$d"; run cp -a "$s" "$d"; }
# link_file SRC DST: backup DST then symlink.
link_file() { local s="$1" d="$2"; backup "$d"; run mkdir -p "$(dirname "$d")"; run ln -sfn "$s" "$d"; }

# marked_block FILE NAME < content : replace/insert "# >>> ttox:NAME >>>" ... "# <<< ttox:NAME <<<"
marked_block() {
  local f="$1" name="$2" body tmp; body="$(cat)"; backup "$f"
  if [ "$TTOX_DRY_RUN" = 1 ]; then printf '  [dry-run] update block ttox:%s in %s\n' "$name" "$f" >&2; return 0; fi
  mkdir -p "$(dirname "$f")"; touch "$f"; tmp="$(mktemp)"
  awk -v s="# >>> ttox:$name >>>" -v e="# <<< ttox:$name <<<" '$0==s{skip=1;next} $0==e{skip=0;next} !skip' "$f" >"$tmp"
  { cat "$tmp"; printf '%s\n%s\n%s\n' "# >>> ttox:$name >>>" "$body" "# <<< ttox:$name <<<"; } >"$f"; rm -f "$tmp"
}
remove_block() { local f="$1" name="$2" tmp; [ -f "$f" ] || return 0; [ "$TTOX_DRY_RUN" = 1 ] && return 0; tmp="$(mktemp)"
  awk -v s="# >>> ttox:$name >>>" -v e="# <<< ttox:$name <<<" '$0==s{skip=1;next} $0==e{skip=0;next} !skip' "$f" >"$tmp"; cat "$tmp" >"$f"; rm -f "$tmp"; }

# state_get KEY / state_set KEY VALUE  (flat key = "value" TOML)
state_get() { [ -f "$TTOX_STATE" ] || return 1; sed -n "s/^$1 = \"\(.*\)\"$/\1/p" "$TTOX_STATE" | head -n1; }
state_set() { [ "$TTOX_DRY_RUN" = 1 ] && return 0; mkdir -p "$TTOX_CONFIG"; touch "$TTOX_STATE"
  local tmp; tmp="$(mktemp)"; grep -v "^$1 = " "$TTOX_STATE" >"$tmp" || true; printf '%s = "%s"\n' "$1" "$2" >>"$tmp"; cat "$tmp" >"$TTOX_STATE"; rm -f "$tmp"; }

# colors_dir VARIANT MODE -> path of generated runtime colours
colors_dir() { printf '%s/core/colors/ttox-%s-%s' "$TTOX_DIST" "$1" "$2"; }
# Applier exit codes: 0 full, 10 partial (print "TIER=<n> REASON=<text>" on stdout), 1 failed.
