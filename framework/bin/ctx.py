#!/usr/bin/env python3
"""Report how much of the Claude Code context window is used / left — for the SDE autonomy guard.

It reads the per-turn token usage Claude Code records in the session transcript (the SAME data the
status line is fed). A turn's context size is the prompt that was sent that turn:
    input_tokens + cache_read_input_tokens + cache_creation_input_tokens
(output_tokens are the reply, not part of the next turn's context). This reads the LAST turn that
has a usage record — the most recent measurement.

THE WINDOW IS AUTO-DETECTED, not assumed. The transcript's `model` field does NOT record the
200k-vs-1M "[1m]" variant (both log `claude-opus-4-8`), so the window cannot be read off the model.
Instead it is inferred from evidence in the transcript:
  • the high-water mark of context size ever observed is a hard LOWER BOUND on the window
    (a 200k window physically cannot hold >200k tokens), and
  • a past auto-compaction's `compactMetadata.preTokens` is a near-exact ceiling probe.
The smallest known window (200000, 1000000) that fits the evidence is chosen. With no evidence yet
(a fresh session) it defaults to the SMALLER window ON PURPOSE — that makes the caller OVER-fire
(ask early — safe) rather than UNDER-fire (sail silently past the real limit and never ask). The
basis is reported as `detected` (evidence forced it) or `assumed` (fail-safe default — could be a
fresh 1M session); `override` when you pin it with --limit or CONTEXT_LIMIT.

The most authoritative source is the OPTIONAL status-line bridge (`--cache`): wired into the status
line, it captures Claude Code's own `context_window.context_window_size` (which knows 200k vs 1M
exactly) to ~/.claude/.ctx-<session>.json. Since the window is stable for a session, this tool reads
the window from that cache (basis `statusline`) while taking `used` fresh from the transcript.
Precedence: --limit/CONTEXT_LIMIT  >  status-line cache  >  transcript inference.

Two transcript-locating modes, auto-detected:
  • status-line mode — Claude Code pipes its status JSON on stdin; we read `transcript_path`.
  • standalone mode  — no stdin; we find the newest transcript for $PWD's project under
    ~/.claude/projects/<encoded-cwd>/.

Examples:
  python3 ctx.py            # -> ctx 91% left  (86k/1000k used, 9%)  [window 1M · detected]
  python3 ctx.py --json     # -> {"used":...,"limit":1000000,"pct_left":91.4,"window":"1M","basis":"detected"}
  CONTEXT_LIMIT=200000 python3 ctx.py        # pin the window explicitly
"""
import argparse
import glob
import json
import os
import sys
import time

KNOWN_WINDOWS = (200_000, 1_000_000)   # the windows Claude Code ships; smallest-that-fits is chosen


def _iter(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def newest_transcript_for_cwd(cwd):
    # Claude Code stores transcripts at ~/.claude/projects/<enc>/<session>.jsonl,
    # where <enc> is the absolute project path with '/' and '.' replaced by '-'.
    enc = cwd.replace('/', '-').replace('.', '-')
    base = os.path.expanduser(os.path.join('~/.claude/projects', enc))
    files = glob.glob(os.path.join(base, '*.jsonl'))
    return max(files, key=os.path.getmtime) if files else None


def _used(usage):
    return (usage.get('input_tokens', 0)
            + usage.get('cache_read_input_tokens', 0)
            + usage.get('cache_creation_input_tokens', 0))


def last_usage(path):
    """Return the usage dict of the most recent message that has one."""
    found = None
    for obj in _iter(path):
        usage = (obj.get('message') or {}).get('usage')
        if isinstance(usage, dict) and (
            'input_tokens' in usage or 'cache_read_input_tokens' in usage
        ):
            found = usage
    return found


def detect_window(path):
    """Infer the context window from transcript evidence. Returns (limit, basis, high_water).

    high_water = the largest context size ever observed (a usage record OR a past auto-compaction's
    preTokens). The chosen window is the smallest KNOWN_WINDOWS value that can contain it; when the
    evidence fits the SMALLEST window we report `assumed` (it is the fail-safe guess, not proven —
    a fresh 1M session also fits), otherwise `detected` (a larger window was forced by evidence)."""
    hi = 0
    for obj in _iter(path):
        u = (obj.get('message') or {}).get('usage')
        if isinstance(u, dict):
            hi = max(hi, _used(u))
        cm = obj.get('compactMetadata')                       # a past auto-compaction ≈ the ceiling
        if isinstance(cm, dict) and cm.get('trigger') == 'auto':
            hi = max(hi, cm.get('preTokens', 0) or 0)
    for w in KNOWN_WINDOWS:
        if hi <= w * 1.02:                                    # 2% slack for reporting jitter
            return w, ('assumed' if w == KNOWN_WINDOWS[0] else 'detected'), hi
    return KNOWN_WINDOWS[-1], 'detected', hi


def _cached_window_for(transcript):
    """The authoritative `context_window_size` from a status-line bridge cache (see --cache) whose
    transcript matches `transcript`. The window is stable for a session, so cache staleness is
    irrelevant here — we only take the window from it. Returns None if no bridge is installed."""
    try:
        files = glob.glob(os.path.expanduser('~/.claude/.ctx-*.json'))
    except Exception:
        return None
    want = os.path.basename(transcript or '')      # <session-uuid>.jsonl — globally unique; matching on
    best = None                                     # the basename dodges every dir-encoding quirk (the
    for p in files:                                 # cache's path comes from Claude Code, ours from a glob)
        try:
            with open(p) as f:
                d = json.load(f)
        except Exception:
            continue
        tp = d.get('transcript_path') or ''
        if want and os.path.basename(tp) == want and d.get('context_window_size'):
            ts = d.get('ts', 0) or 0
            if best is None or ts > best[0]:
                best = (ts, int(d['context_window_size']))
    return best[1] if best else None


def _cache_mode():
    """Status-line TEE: persist the piped status JSON's context_window, then re-emit stdin unchanged
    so a downstream renderer (e.g. ccstatusline) still receives it. Never fails loudly — a non-zero
    exit would blank the user's status line."""
    raw = '' if sys.stdin.isatty() else sys.stdin.read()
    try:
        d = json.loads(raw) if raw.strip() else {}
        cw = d.get('context_window') or {}
        sid = d.get('session_id') or 'default'
        rec = {'session_id': sid, 'transcript_path': d.get('transcript_path'),
               'context_window_size': cw.get('context_window_size'),
               'used_percentage': cw.get('used_percentage'),
               'remaining_percentage': cw.get('remaining_percentage'),
               'total_input_tokens': cw.get('total_input_tokens'),
               'ts': time.time()}
        dst = os.path.expanduser('~/.claude/.ctx-%s.json' % sid)
        tmp = '%s.%d.tmp' % (dst, os.getpid())
        with open(tmp, 'w') as f:
            json.dump(rec, f)
        os.replace(tmp, dst)             # atomic — a cancelled in-flight status line can't leave a torn cache
    except Exception:
        pass
    sys.stdout.write(raw)
    return 0


def main():
    ap = argparse.ArgumentParser(description='Context-window usage for the current Claude Code session.')
    ap.add_argument('--limit', type=int, default=None,
                    help='window size in tokens — overrides auto-detect (or set CONTEXT_LIMIT)')
    ap.add_argument('--transcript', help='path to a specific transcript .jsonl')
    ap.add_argument('--cache', action='store_true',
                    help='status-line TEE: persist the piped status JSON context_window to '
                         '~/.claude/.ctx-<session>.json, then re-emit stdin for the downstream renderer')
    ap.add_argument('--json', action='store_true', help='emit machine-readable JSON')
    args = ap.parse_args()

    if args.cache:                 # wired into the status line; not a reporting call
        return _cache_mode()

    transcript = args.transcript
    # status-line mode: Claude Code pipes {"transcript_path": ..., ...} on stdin
    if not transcript and not sys.stdin.isatty():
        try:
            transcript = (json.load(sys.stdin) or {}).get('transcript_path')
        except Exception:
            transcript = None
    if not transcript:
        transcript = newest_transcript_for_cwd(os.getcwd())

    if not transcript or not os.path.exists(transcript):
        print('ctx: ? (no transcript found)')
        return 1

    usage = last_usage(transcript)
    if not usage:
        print('ctx: ? (no usage record in transcript)')
        return 1
    used = _used(usage)

    # window precedence: explicit override (flag/env) > status-line bridge cache (Claude Code's own
    # authoritative context_window_size) > inference from transcript evidence (fail-safe).
    env = os.environ.get('CONTEXT_LIMIT')
    cached = _cached_window_for(transcript)
    if args.limit:
        limit, basis = args.limit, 'override'
    elif env and env.strip().isdigit():
        limit, basis = int(env.strip()), 'override'
    elif cached:
        limit, basis = cached, 'statusline'
    else:
        limit, basis, _hi = detect_window(transcript)

    pct_used = used / limit * 100 if limit else 0
    pct_left = max(0.0, 100 - pct_used)
    win = '1M' if limit >= 1_000_000 else ('%dk' % (limit // 1000))

    if args.json:
        print(json.dumps({'used': used, 'limit': limit, 'pct_used': round(pct_used, 1),
                          'pct_left': round(pct_left, 1), 'window': win, 'basis': basis}))
    else:
        k = lambda n: '%dk' % (n / 1000)
        print('ctx %d%% left  (%s/%s used, %d%%)  [window %s · %s]'
              % (pct_left, k(used), k(limit), pct_used, win, basis))
    return 0


if __name__ == '__main__':
    sys.exit(main())
