"""Tests for the `sde` deriver — every rung of the ladder + the tricky drift cases.

The prior-art CLI shipped untested (its own KNOWN-ISSUES O-2). This is the regression net that
keeps the derived state machine honest. stdlib `unittest`; run: python3 -m unittest test_sde
"""
import importlib.machinery, importlib.util, json, os, shutil, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SDE_PATH = os.path.join(HERE, "..", "bin", "sde")


def _load():
    loader = importlib.machinery.SourceFileLoader("sde_mod", SDE_PATH)
    spec = importlib.util.spec_from_loader("sde_mod", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


sde = _load()

SPEC_BOUND = ("# Slice\n## Intents\nI1. do the thing.\n"
              "    eval: contract evals/I1.x.py gate=required mutant=evals/I1.mutant.diff\n")
TASKS_HDR = ("# Tasks\n| id | targets | deps | status | owner@ts |\n"
             "|----|---------|------|--------|----------|\n")


class LadderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, ".sde")
        self.sdir = os.path.join(self.root, "slices", "01-x")
        os.makedirs(self.sdir)
        os.makedirs(os.path.join(self.tmp, "evals"))   # eval code lives at PROJECT ROOT, not in .sde/
        self._w("objective.md", "# Objective: Test\nNorth star: x.\nDone when:\n- x\n")
        self._w("runs.log", "# header\n")
        self._ws("tasks.md", TASKS_HDR)
        self._ws("trust.log", "# header\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _w(self, rel, c):
        with open(os.path.join(self.root, rel), "w") as f:
            f.write(c)

    def _ws(self, rel, c):
        with open(os.path.join(self.sdir, rel), "w") as f:
            f.write(c)

    def _we(self, name, c):                            # write an eval file at project root
        with open(os.path.join(self.tmp, "evals", name), "w") as f:
            f.write(c)

    def _app(self, rel, line, base=None):
        with open(os.path.join(base or self.sdir, rel), "a") as f:
            f.write(line + "\n")

    def _phase(self):
        return sde.slice_phase(self.root, "01-x", self.sdir)[0]

    def _establish_trust(self):
        eh = sde._sha(os.path.join(self.tmp, "evals", "I1.x.py"))
        fp = sde.spec_fingerprint(self.sdir)
        self._app("trust.log", json.dumps({"eval": "I1.contract", "result": "killed",
                                            "eval_hash": eh, "spec_fp": fp}))
        self._app("trust.log", json.dumps({"eval": "I1.contract", "result": "passed",
                                            "eval_hash": eh, "spec_fp": fp}))
        return fp

    def test_full_ladder(self):
        self.assertEqual(self._phase(), "spec")                       # rung 0: no spec.md

        self._ws("spec.md", "# Slice\n## Intents\nI1. do the thing.\n")
        self.assertEqual(self._phase(), "bind")                       # rung 1: intent unbound

        self._ws("spec.md", SPEC_BOUND)
        self._we("I1.x.py","# eval v1\n")
        self.assertEqual(self._phase(), "trust")                      # rung 2: no trust evidence

        fp = self._establish_trust()
        self.assertEqual(self._phase(), "freeze")                     # rung 3: trusted, not frozen

        shutil.copy(os.path.join(self.sdir, "spec.md"), os.path.join(self.sdir, "spec.lock.md"))
        self._app("tasks.md", "| T-01 | I1 | - | todo | - |")
        self.assertEqual(self._phase(), "execute")                    # rung 4: task ready

        self._ws("tasks.md", TASKS_HDR + "| T-01 | I1 | - | done | a@t |\n")
        self.assertEqual(self._phase(), "evalrun")                    # rung 5: no PASS run yet

        self._app("runs.log", json.dumps({"slice": "01-x", "eval": "I1.contract",
                                           "verdict": "PASS", "spec_fp": fp}), base=self.root)
        self.assertEqual(self._phase(), "done")                       # rung 6: complete

    def test_trust_goes_stale_when_eval_changes(self):
        self._ws("spec.md", SPEC_BOUND)
        self._we("I1.x.py","# eval v1\n")
        self._establish_trust()
        self.assertEqual(self._phase(), "freeze")                     # trusted
        self._we("I1.x.py","# eval v2 — CHANGED\n")            # eval_hash drifts
        self.assertEqual(self._phase(), "trust")                      # → stale → rung 2 re-opens
        self.assertEqual(sde.derive_trust(self.root, self.sdir, sde.parse_spec(self.sdir))["I1.contract"], "stale")

    def test_blocked_when_spec_drifts_after_freeze(self):
        # freeze at intent-v0, then change the intent AND re-establish trust at the new fp,
        # but do NOT re-freeze → rung 2 passes, rung 3 sees lock != spec → blocked.
        self._ws("spec.md", SPEC_BOUND)
        self._we("I1.x.py","# eval\n")
        self._establish_trust()
        shutil.copy(os.path.join(self.sdir, "spec.md"), os.path.join(self.sdir, "spec.lock.md"))
        # change the intent text (drift), re-establish trust at the NEW fingerprint
        self._ws("spec.md", SPEC_BOUND.replace("do the thing", "do the OTHER thing"))
        self._establish_trust()
        self.assertEqual(self._phase(), "blocked")

    def test_objective_next_action_picks_first_unfinished_slice(self):
        # slice 01 done; slice 02 only has an intent (rung 1) → next action is for 02
        self._ws("spec.md", SPEC_BOUND)
        self._we("I1.x.py","# eval\n")
        fp = self._establish_trust()
        shutil.copy(os.path.join(self.sdir, "spec.md"), os.path.join(self.sdir, "spec.lock.md"))
        self._ws("tasks.md", TASKS_HDR + "| T-01 | I1 | - | done | a@t |\n")
        self._app("runs.log", json.dumps({"slice": "01-x", "eval": "I1.contract",
                                           "verdict": "PASS", "spec_fp": fp}), base=self.root)
        self.assertEqual(self._phase(), "done")
        s2 = os.path.join(self.root, "slices", "02-y")
        os.makedirs(os.path.join(s2, "evals"))
        with open(os.path.join(s2, "spec.md"), "w") as f:
            f.write("# Slice 2\n## Intents\nI1. another thing.\n")
        sid, phase, action, detail = sde.next_action(self.root)
        self.assertEqual((sid, phase), ("02-y", "bind"))

    def test_malformed_log_lines_are_skipped(self):
        self._ws("spec.md", SPEC_BOUND)
        self._we("I1.x.py","# eval\n")
        self._app("trust.log", "{ this is not valid json")             # torn write
        self._establish_trust()
        self._app("trust.log", "")                                     # blank
        self.assertEqual(self._phase(), "freeze")                      # still derives trust cleanly

    def test_non_dir_entries_in_slices_are_ignored(self):
        # macOS .DS_Store (and .blocked markers, editor cruft) must not be treated as slices
        self._ws("spec.md", "# S\n## Intents\nI1. x.\n")
        with open(os.path.join(self.root, "slices", ".DS_Store"), "wb") as f:
            f.write(b"\x00\x01\x02")
        self.assertEqual(sde.slices(self.root), ["01-x"])
        sid, phase, _, _ = sde.next_action(self.root)
        self.assertEqual(sid, "01-x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
