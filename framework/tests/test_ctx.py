"""Tests for ctx.py window auto-detection — the safety-critical bit.

A WRONG window silently no-ops the autonomy guard (it would report plenty of room while the real
window fills, so the 25%-left ASK never fires and the session dies un-asked). So the fail-safe
must hold: when the evidence is ambiguous, pick the SMALLER window (over-ASK, safe) — never the
larger (silent death). stdlib `unittest`; run: python3 -m unittest test_ctx
"""
import importlib.machinery, importlib.util, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CTX_PATH = os.path.join(HERE, "..", "skills", "sde-auto", "ctx.py")   # bundled with the /sde-auto skill


def _load():
    loader = importlib.machinery.SourceFileLoader("ctx_mod", CTX_PATH)
    spec = importlib.util.spec_from_loader("ctx_mod", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


ctx = _load()


def _transcript(objs):
    fd, p = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    with open(p, "w") as f:
        for o in objs:
            f.write(json.dumps(o) + "\n")
    return p


def U(n):                                            # a usage-bearing transcript line of `n` ctx tokens
    return {"message": {"usage": {"input_tokens": n}}}


class DetectWindow(unittest.TestCase):
    def test_no_evidence_failsafe_to_smaller(self):
        # a fresh/small session — no proof of a big window → assume the SMALLER one (safe, over-ASKs)
        p = _transcript([U(50_000)]); self.addCleanup(os.remove, p)
        self.assertEqual(ctx.detect_window(p)[:2], (200_000, "assumed"))

    def test_used_above_200k_forces_1m(self):
        # a 200k window physically cannot hold >200k tokens → evidence FORCES the 1M window
        p = _transcript([U(250_000), U(60_000)]); self.addCleanup(os.remove, p)
        self.assertEqual(ctx.detect_window(p)[:2], (1_000_000, "detected"))

    def test_auto_compaction_pretokens_probe_1m(self):
        # a past auto-compaction's preTokens ≈ the ceiling; 993745 ⇒ this was a 1M session
        p = _transcript([{"compactMetadata": {"trigger": "auto", "preTokens": 993_745}}, U(80_000)])
        self.addCleanup(os.remove, p)
        self.assertEqual(ctx.detect_window(p)[:2], (1_000_000, "detected"))

    def test_200k_session_that_compacted_stays_200k(self):
        # a real 200k session that auto-compacted at ~190k must NOT be mistaken for 1M
        p = _transcript([{"compactMetadata": {"trigger": "auto", "preTokens": 190_000}}, U(55_000)])
        self.addCleanup(os.remove, p)
        self.assertEqual(ctx.detect_window(p)[:2], (200_000, "assumed"))

    def test_last_usage_is_the_most_recent(self):
        # pct is computed from the LATEST measurement, not the high-water mark
        p = _transcript([U(250_000), U(60_000)]); self.addCleanup(os.remove, p)
        self.assertEqual(ctx._used(ctx.last_usage(p)), 60_000)


class StatusLineBridge(unittest.TestCase):
    def test_cache_mode_writes_window_and_passes_stdin_through(self):
        import subprocess, shutil
        home = tempfile.mkdtemp(); os.makedirs(os.path.join(home, ".claude"))
        self.addCleanup(shutil.rmtree, home)
        payload = json.dumps({"session_id": "sid1", "transcript_path": "/tmp/t.jsonl",
                              "context_window": {"context_window_size": 1_000_000, "used_percentage": 12.5,
                                                 "remaining_percentage": 87.5, "total_input_tokens": 125000}})
        r = subprocess.run([sys.executable, CTX_PATH, "--cache"], input=payload, text=True,
                           capture_output=True, env={**os.environ, "HOME": home})
        self.assertEqual(r.stdout, payload)                       # re-emits stdin verbatim for the renderer
        with open(os.path.join(home, ".claude", ".ctx-sid1.json")) as cf:
            cache = json.load(cf)
        self.assertEqual(cache["context_window_size"], 1_000_000)
        self.assertEqual(cache["transcript_path"], "/tmp/t.jsonl")

    def test_statusline_cache_overrides_failsafe(self):
        # transcript alone (120k used, no big-window evidence) infers 200k 'assumed'; an installed
        # bridge cache carrying Claude Code's authoritative 1M window must WIN (basis 'statusline').
        import subprocess, shutil
        home = tempfile.mkdtemp(); os.makedirs(os.path.join(home, ".claude"))
        self.addCleanup(shutil.rmtree, home)
        tr = _transcript([U(120_000)]); self.addCleanup(os.remove, tr)
        # cache stores a DIFFERENT directory prefix but the SAME <session>.jsonl basename — the match
        # must succeed on basename alone (mirrors a real run: Claude Code's path ≠ our glob-resolved one).
        cache_tp = os.path.join("/elsewhere/projects/enc", os.path.basename(tr))
        with open(os.path.join(home, ".claude", ".ctx-s.json"), "w") as cf:
            json.dump({"session_id": "s", "transcript_path": cache_tp,
                       "context_window_size": 1_000_000, "ts": 1}, cf)
        env = {k: v for k, v in os.environ.items() if k != "CONTEXT_LIMIT"}; env["HOME"] = home
        r = subprocess.run([sys.executable, CTX_PATH, "--json", "--transcript", tr],
                           text=True, capture_output=True, env=env)
        d = json.loads(r.stdout)
        self.assertEqual((d["limit"], d["basis"]), (1_000_000, "statusline"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
