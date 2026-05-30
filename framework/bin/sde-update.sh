#!/usr/bin/env bash
# sde-update.sh — update the vendored SDE framework from its source GitHub repo, PRESERVING all
# project state in .sde/. Run from the PROJECT ROOT (the dir containing framework/ and .sde/).
#
#   bash framework/bin/sde-update.sh --check   # compare versions only; no changes.
#                                              # exit 0 = up-to-date · 2 = update available · 1 = error
#   bash framework/bin/sde-update.sh           # apply the update IF one is available
#
# REPLACES (framework artifacts only): framework/{bin,templates,skills,tests,VERSION,REPO},
#   FRAMEWORK.md, the installed .claude/skills/sde-*, and .sde/RESUME.md (the protocol doc).
# NEVER TOUCHES your project state: .sde/{objective.md,decisions.md,runs.log,handoff.md,slices/}.
set -u
MODE="${1:-apply}"
ROOT="$PWD"; FW="$ROOT/framework"
[ -f "$FW/bin/sde" ] || { echo "error: run from the project root (no framework/bin/sde here)" >&2; exit 1; }

REPO="${SDE_UPDATE_REPO:-$(cat "$FW/REPO" 2>/dev/null || echo 'gunawanwilljkt/spec-driven-with-evals@main')}"
SLUG="${REPO%@*}"; BR="${REPO##*@}"; [ "$BR" = "$REPO" ] && BR=main

cur="$(cat "$FW/VERSION" 2>/dev/null | tr -d '[:space:]')"; [ -n "$cur" ] || cur="0.0.0"
latest="$(curl -fsSL "https://raw.githubusercontent.com/$SLUG/$BR/framework/VERSION" 2>/dev/null | tr -d '[:space:]')"
[ -n "$latest" ] || { echo "error: could not read latest VERSION from $SLUG@$BR (offline? repo missing framework/VERSION?)" >&2; exit 1; }
echo "current: ${cur:-0.0.0}    latest: $latest    source: $SLUG@$BR"

# portable (BSD/GNU) semver compare for X.Y.Z — is $1 strictly newer than $2 ?
newer(){ [ "$1" != "$2" ] && [ "$(printf '%s\n%s\n' "$1" "$2" | sort -t. -k1,1n -k2,2n -k3,3n | tail -1)" = "$1" ]; }
if ! newer "$latest" "${cur:-0.0.0}"; then echo "UP-TO-DATE — nothing to update."; exit 0; fi
echo "UPDATE-AVAILABLE: ${cur:-0.0.0} -> $latest"
[ "$MODE" = "--check" ] && exit 2

# ── apply ────────────────────────────────────────────────────────────────────────────────────────
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
echo "fetching $SLUG@$BR ..."
curl -fsSL "https://codeload.github.com/$SLUG/tar.gz/refs/heads/$BR" | tar -xz -C "$TMP" || { echo "error: download/extract failed" >&2; exit 1; }
SRC="$(echo "$TMP"/*/)"; SRC="${SRC%/}"
# sanity: the fetched tree must look like the framework BEFORE we touch anything local
[ -f "$SRC/framework/bin/sde" ] && [ -f "$SRC/framework/VERSION" ] || { echo "error: fetched tree is not a valid SDE framework; aborting (nothing changed)" >&2; exit 1; }

echo "replacing framework artifacts (your .sde/ project state is preserved) ..."
for item in framework/bin framework/templates framework/skills framework/tests framework/VERSION framework/REPO FRAMEWORK.md; do
  [ -e "$SRC/$item" ] || continue
  rm -rf "${ROOT:?}/$item"; mkdir -p "$ROOT/$(dirname "$item")"; cp -R "$SRC/$item" "$ROOT/$item"
done
chmod +x "$FW/bin/"* 2>/dev/null

# re-install the slash-command skills so Claude Code discovers the new versions
if [ -d "$ROOT/.claude/skills" ]; then
  for s in "$FW"/skills/sde-*/; do [ -d "$s" ] || continue; n="$(basename "$s")"; rm -rf "$ROOT/.claude/skills/$n"; cp -R "$s" "$ROOT/.claude/skills/$n"; done
fi

# refresh ONLY the protocol doc in .sde/ (RESUME.md is a framework artifact, not your project state)
[ -f "$FW/templates/.sde/RESUME.md" ] && [ -d "$ROOT/.sde" ] && cp "$FW/templates/.sde/RESUME.md" "$ROOT/.sde/RESUME.md"

echo "verifying the updated framework ..."
ok=1
python3 "$FW/tests/test_sde.py" >/dev/null 2>&1 && echo "  deriver tests: OK" || { echo "  deriver tests: FAILED"; ok=0; }
python3 "$FW/bin/sde" status --root "$ROOT" >/dev/null 2>&1; drc=$?   # 0=complete, 2=work remains: both fine; 1=structural error
if [ "$drc" = 0 ] || [ "$drc" = 2 ]; then echo "  project state still derives: OK"; else echo "  project derive: CHECK MANUALLY (rc=$drc)"; ok=0; fi
echo "updated ${cur:-0.0.0} -> $latest. Project state in .sde/ preserved."
[ "$ok" = 1 ] || { echo "WARNING: post-update checks failed — review, or roll back with: git checkout -- framework FRAMEWORK.md .claude .sde/RESUME.md" >&2; exit 1; }
echo "DONE."
