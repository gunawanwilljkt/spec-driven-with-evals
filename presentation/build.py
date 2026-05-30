#!/usr/bin/env python3
"""Generator for the SDE presentation. One content source → 3 themed HTML files
(dark / light / print-no-background). Run: python3 build.py [--debug]

--debug renders content-box outlines and DISABLES clipping so overflow is visible in screenshots
(a clean screenshot must mean clean layout, not silently-clipped text).
"""
import sys
DEBUG = "--debug" in sys.argv

# ── Themes (only CSS variables differ between the three files) ───────────────
THEMES = {
    "dark": {"bg": "#0b0f17", "bg2": "#070a10", "panel": "#131c2b", "panel2": "#0f1724",
             "ink": "#e8eef7", "muted": "#8a98ab", "line": "#243042", "accent": "#8aa2ff",
             "accent2": "#5ed3c2", "pass": "#3ddc97", "fail": "#ff7d7d", "warn": "#ffd166",
             "codebg": "#0c1320", "codeink": "#cfdbea", "brand": "#94a3b6", "chiptext": "#07120c",
             "shadow": "0 14px 40px rgba(0,0,0,.40)", "glow": "0 0 0 1px rgba(138,162,255,.10)"},
    "light": {"bg": "#eceff4", "bg2": "#e3e8f0", "panel": "#ffffff", "panel2": "#f6f8fb",
              "ink": "#1b2433", "muted": "#5c6675", "line": "#e3e8f0", "accent": "#4d68ff",
              "accent2": "#11a597", "pass": "#0f9a64", "fail": "#df4f64", "warn": "#9c7414",
              "codebg": "#f3f6fa", "codeink": "#283243", "brand": "#7b8696", "chiptext": "#ffffff",
              "shadow": "0 10px 30px rgba(20,30,50,.10)", "glow": "0 0 0 1px rgba(77,104,255,.08)"},
    "print": {"bg": "#ffffff", "bg2": "#ffffff", "panel": "#ffffff", "panel2": "#ffffff",
              "ink": "#10141a", "muted": "#555c66", "line": "#c7cdd6", "accent": "#26439c",
              "accent2": "#0a7d72", "pass": "#0a7a4c", "fail": "#bb3322", "warn": "#6f5712",
              "codebg": "#f5f7f9", "codeink": "#1b2129", "brand": "#666", "chiptext": "#ffffff",
              "shadow": "none", "glow": "none"},
}

BASE_CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-snap-type:y mandatory;scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;font-feature-settings:'cv02','cv03','ss01'}
.deck{display:flex;flex-direction:column;align-items:center}
.slide{position:relative;width:1280px;height:720px;flex:0 0 auto;
  background:radial-gradient(1200px 600px at 78% -8%, var(--panel2), var(--bg) 60%);
  scroll-snap-align:center;overflow:hidden;border-bottom:1px solid var(--bg2)}
.slide-in{position:absolute;inset:0;padding:58px 74px 54px;display:flex;flex-direction:column}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);
  display:flex;align-items:center;gap:10px}
.eyebrow::before{content:"";width:22px;height:2px;background:var(--accent);display:inline-block;border-radius:2px}
.s-title{font-size:38px;line-height:1.12;font-weight:800;letter-spacing:-.02em;margin-top:12px;max-width:1010px}
.s-title .hl{color:var(--accent)}
.s-body{flex:1;margin-top:26px;min-height:0;display:flex;flex-direction:column;justify-content:flex-start}
.s-foot{position:absolute;left:74px;right:74px;bottom:24px;display:flex;justify-content:space-between;
  align-items:center;font-size:12px;color:var(--brand);letter-spacing:.02em}
.s-foot .pg{font-variant-numeric:tabular-nums;font-weight:600}
.lead{font-size:22px;line-height:1.5;color:var(--ink);max-width:980px;font-weight:450}
.lead .mut,.mut{color:var(--muted)}.accent{color:var(--accent)}.ok{color:var(--pass)}.bad{color:var(--fail)}.warn{color:var(--warn)}
.sub{font-size:17px;line-height:1.5;color:var(--muted);max-width:980px}
b,strong{font-weight:700}
.grid{display:grid;gap:16px}.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:1fr 1fr 1fr}.g4{grid-template-columns:1fr 1fr 1fr 1fr}
.g12{grid-template-columns:1.05fr .95fr}.g21{grid-template-columns:1.3fr 1fr}.g31{grid-template-columns:1.55fr 1fr}
.stack{display:flex;flex-direction:column;gap:13px}.row{display:flex;gap:12px;align-items:center}.wrap{flex-wrap:wrap}
.card{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:20px;box-shadow:var(--shadow)}
.card .k{font-size:12px;font-weight:700;letter-spacing:.11em;text-transform:uppercase;color:var(--accent2)}
.card h3{font-size:19px;font-weight:750;margin:8px 0 6px;letter-spacing:-.01em}
.card p{font-size:15.5px;line-height:1.5;color:var(--muted)}
.card.tight{padding:16px 17px}.card.tight h3{font-size:17px;margin:6px 0 4px}.card.tight p{font-size:14.5px}
.num{width:28px;height:28px;border-radius:8px;background:var(--panel2);border:1px solid var(--line);
  color:var(--accent);font-weight:800;font-size:14px;display:grid;place-items:center;flex:0 0 auto}
.code{background:var(--codebg);border:1px solid var(--line);border-radius:13px;padding:15px 17px;
  font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:14px;line-height:1.6;color:var(--codeink);white-space:pre;overflow:hidden;tab-size:2}
.code.sm{font-size:13px;line-height:1.55}
.k-{color:var(--accent);font-weight:600}.m-{color:var(--fail);font-weight:600}.o-{color:var(--pass);font-weight:600}
.c-{color:var(--muted)}.s-{color:var(--accent2);font-weight:600}
.codecap{font-size:13px;color:var(--muted);margin-top:8px;line-height:1.45}
.filetag{font-size:11.5px;color:var(--brand);font-family:'JetBrains Mono',monospace;margin-bottom:7px;display:block;letter-spacing:.02em}
.truth{display:grid;grid-template-columns:auto 1fr 1fr;gap:9px;align-items:center;max-width:540px}
.truth.wide{max-width:600px}
.truth .h{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);text-align:center}
.truth .rl{font-size:15px;font-weight:650;color:var(--ink)}
.truth .cell{display:grid;place-items:center;background:var(--panel);border:1px solid var(--line);border-radius:10px;height:46px}
.chip{font-size:13px;font-weight:800;letter-spacing:.04em;padding:5px 12px;border-radius:999px}
.chip.pass{background:var(--pass);color:var(--chiptext)}.chip.fail{background:var(--fail);color:var(--chiptext)}
.chip.gho{background:transparent;border:1.5px solid var(--line);color:var(--muted)}
.badge{font-size:11.5px;font-weight:750;letter-spacing:.03em;padding:5px 11px;border-radius:999px;
  border:1px solid var(--line);background:var(--panel2);color:var(--muted);white-space:nowrap}
.badge.be{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 35%,var(--line))}
.badge.mob{color:var(--accent2);border-color:color-mix(in srgb,var(--accent2) 35%,var(--line))}
.badge.adm{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 35%,var(--line))}
.badge.live{color:var(--pass);border-color:color-mix(in srgb,var(--pass) 40%,var(--line))}
.badge.illus{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 40%,var(--line))}
.badges{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.head-row{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}
.ladder{display:flex;flex-direction:column;gap:6px}
.rung{display:grid;grid-template-columns:26px 104px 1fr;gap:13px;align-items:center;
  background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:7px 13px}
.rung .ph{font-weight:750;font-size:14.5px}.rung .gd{font-size:13.5px;color:var(--muted)}
.rung.on{border-color:var(--accent);box-shadow:var(--glow)}.rung.done .ph{color:var(--pass)}
.cmd{font-family:'JetBrains Mono',monospace;font-size:13.5px;background:var(--panel);border:1px solid var(--line);
  border-radius:7px;padding:3px 9px;color:var(--accent);white-space:nowrap}
.flow{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.flow .arr{color:var(--muted);font-size:15px}
.pill{display:inline-flex;align-items:center;gap:8px;background:var(--panel);border:1px solid var(--line);
  border-radius:999px;padding:7px 14px;font-size:14px;font-weight:600}
.pill.ac{border-color:color-mix(in srgb,var(--accent) 40%,var(--line));color:var(--accent)}
.dot{width:8px;height:8px;border-radius:50%;flex:0 0 auto}
.note{font-size:13px;color:var(--muted);line-height:1.45}
.note.illus{border-left:3px solid var(--warn);background:color-mix(in srgb,var(--warn) 8%,transparent);
  border-radius:0 8px 8px 0;padding:9px 13px}
.kpi{font-size:32px;font-weight:850;letter-spacing:-.02em;line-height:1}.kpi.ok{color:var(--pass)}.kpi.ac{color:var(--accent)}
.kpi-l{font-size:13px;color:var(--muted);margin-top:5px;line-height:1.35}
ul.bul{list-style:none;display:flex;flex-direction:column;gap:11px}
ul.bul li{position:relative;padding-left:25px;font-size:17.5px;line-height:1.42;color:var(--ink)}
ul.bul li::before{content:"";position:absolute;left:0;top:8px;width:8px;height:8px;border-radius:50%;background:var(--accent)}
ul.bul.sm li{font-size:15.5px}ul.bul.sm li::before{top:7px}
.cover .kick{font-size:14px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);font-weight:700}
.cover h1{font-size:74px;line-height:1.02;font-weight:850;letter-spacing:-.035em;margin:18px 0 0}
.cover h1 .e{color:var(--accent)}
.cover .tag{font-size:23px;color:var(--muted);margin-top:20px;max-width:880px;line-height:1.45}
.cover .meta{margin-top:auto;display:flex;gap:10px;flex-wrap:wrap}
.sec .big{font-size:120px;font-weight:850;letter-spacing:-.04em;color:var(--accent);line-height:.9;opacity:.92}
.sec h2{font-size:44px;font-weight:820;letter-spacing:-.02em;margin-top:6px}
.sec .badges{justify-content:flex-start;margin-top:18px}
.sec p{font-size:18px;color:var(--muted);margin-top:14px;max-width:780px;line-height:1.5}
.statement{display:flex;flex-direction:column;justify-content:center;height:100%}
.statement .q{font-size:40px;line-height:1.26;font-weight:800;letter-spacing:-.02em;max-width:1050px}
.statement .q .hl{color:var(--accent)}
.statement .by{font-size:18px;color:var(--muted);margin-top:22px}
.tier h3{font-size:18px}.bar{height:7px;border-radius:6px;background:var(--panel2);overflow:hidden;border:1px solid var(--line);margin-top:10px}
.bar>i{display:block;height:100%;border-radius:6px;background:var(--accent)}
.surf{display:grid;grid-template-columns:90px 1fr;gap:12px;align-items:center}
"""
DEBUG_CSS = r"""
.slide{overflow:visible !important}
.s-body{outline:1px dashed color-mix(in srgb,var(--fail) 60%,transparent);outline-offset:5px}
.slide-in{outline:1px solid color-mix(in srgb,var(--accent) 45%,transparent)}
"""
PRINT_CSS = r"""
@page{size:1280px 720px;margin:0}
html{scroll-snap-type:none}
body{background:#fff}
.slide{break-after:page;page-break-after:always;border:1px solid var(--line);background:#fff !important}
.slide:last-child{break-after:auto}
"""

# ── component helpers ────────────────────────────────────────────────────────
def truth(rows, head=("correct impl", "the mutant"), wide=False):
    h = f'<div class="h"></div><div class="h">{head[0]}</div><div class="h">{head[1]}</div>'
    cells = ""
    for label, a, b in rows:
        def chip(v):
            c = "pass" if v == "PASS" else ("fail" if v == "FAIL" else "gho")
            return f'<span class="chip {c}">{v}</span>'
        cells += f'<div class="rl">{label}</div><div class="cell">{chip(a)}</div><div class="cell">{chip(b)}</div>'
    return f'<div class="truth{" wide" if wide else ""}">{h}{cells}</div>'

def code(lines, filetag=None, sm=False):
    tag = f'<span class="filetag">{filetag}</span>' if filetag else ""
    return f'<div class="code{" sm" if sm else ""}">{tag}{chr(10).join(lines)}</div>'

def card(k, title, body, cls="tight"):
    return f'<div class="card {cls}"><div class="k">{k}</div><h3>{title}</h3><p>{body}</p>'.rstrip() + "</div>"

ILLUS = ('<div class="note illus"><b>Illustrative walkthrough.</b> Applies the SDE method to a '
         'realistic system; only the pagination example is actually executed in the repo.</div>')

# ── slides ───────────────────────────────────────────────────────────────────
SLIDES = []
def slide(**kw): SLIDES.append(kw)

# INTRO
slide(kind="cover")
slide(kind="statement",
      q='AI now writes working code in seconds. The open question is no longer '
        '<span class="hl">“does it run?”</span> — it’s <span class="hl">“did it build what we meant?”</span>',
      by="SDE moves the unit of trust from a passing test to a trustworthy eval.")
slide(kind="content", eyebrow="The trap", title='“Tests pass” is not “intent satisfied”', body=f"""
<div class="grid g21" style="gap:30px">
  <div class="stack">
    <div class="lead">A unit test checks an <b>example</b>. It can stay green while the code quietly
      betrays the <b>intent</b> — because it never exercised the case that matters.</div>
    <ul class="bul">
      <li>Pagination that <span class="bad">duplicates a row</span> under a concurrent insert</li>
      <li>A query that <span class="bad">leaks another tenant’s data</span></li>
      <li>A charge endpoint that <span class="bad">bills twice</span> on a retry</li>
    </ul>
  </div>
  <div class="stack">
    {truth([("unit test","PASS","PASS"),("the eval","PASS","FAIL")])}
    <div class="note">The mutant is a <b>plausible wrong implementation</b>. The unit test can’t tell
      it apart from the right one. A <b>validity-aware eval</b> can.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="The framework in three ideas", title="Three pillars", body=f"""
<div class="grid g3">
  {card("Pillar 1","Eval validity is the product","An eval is trusted only when it is GREEN-on-right ∧ RED-on-wrong — it passes on the intended code and is proven to FAIL on a plausible mutant.","")}
  {card("Pillar 2","Progressive rigor","One framework, three tiers: Tier 0 convention → Tier 1 gated skills → Tier 2 autonomous factory. You never install machinery you don’t need yet.","")}
  {card("Pillar 3","Proof by dogfooding","It is built using itself. The proof is runnable; resumability is demonstrated by a cold agent recovering state from disk alone.","")}
</div>""")

# HOW IT WORKS
slide(kind="content", eyebrow="How it works", title="The lifecycle: objective → eval-confirmed code", body=f"""
<div class="stack" style="gap:22px">
  <div class="row"><span class="pill ac">OBJECTIVE</span><span class="flow arr">→</span>
    <span class="mut" style="font-size:16px">decomposed into thin vertical <b>slices</b>, each run through:</span></div>
  <div class="flow">
    <span class="pill">spec</span><span class="arr">→</span><span class="pill">bind evals</span><span class="arr">→</span>
    <span class="pill ac">trust</span><span class="arr">→</span><span class="pill">freeze</span><span class="arr">→</span>
    <span class="pill">execute</span><span class="arr">→</span><span class="pill">eval-run</span><span class="arr">→</span>
    <span class="pill" style="border-color:var(--pass);color:var(--pass)">done</span>
  </div>
  <div class="note">Every step is a <b>pure function of disk state</b> — a <span class="cmd" style="padding:1px 7px">grep</span>/<span class="cmd" style="padding:1px 7px">diff</span>/<span class="cmd" style="padding:1px 7px">cat</span>, not a value held in the chat. The chat is a cache; the repo is the memory. A fresh session computes the same “what’s next?”.</div>
</div>""")
slide(kind="content", eyebrow="How it works · the spec", title="A spec is numbered intent statements", body=f"""
<div class="grid g12" style="gap:28px">
  {code(['<span class="c-"># what we MEAN — not how. each intent binds ≥1 eval.</span>',
         'I1. Every item in a paging session is returned',
         '    <span class="o-">exactly once</span> — no omission, no duplicate.',
         '    eval: journey  evals/session.py  gate=<span class="k-">required</span>',
         '          mutant=evals/mutant.diff',
         'I2. Paging is stable under a concurrent insert',
         '    (keyset, not OFFSET).',
         '    eval: journey  evals/session.py  gate=required',
         '    eval: ux       evals/rubric.md   gate=flag'], filetag='.sde/slices/01-pagination/spec.md')}
  <div class="stack">
    {card("Why prose + bindings","Intent, then evidence","Each intent is a single checkable statement. Each binds an eval that must catch a violation of it. Coverage is derived: every intent → ≥1 eval, or the slice can’t advance.","")}
    <div class="note">Gates: <b class="ok">required</b> blocks · <b class="warn">flag</b> surfaces · advisory always allows.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="The centerpiece", title='An eval earns trust: <span class="hl">GREEN-on-right ∧ RED-on-wrong</span>', body=f"""
<div class="grid g12" style="gap:28px">
  <div class="stack">
    {code(['<span class="c-"># the eval (validity-aware)</span>',
           'page 1 → <span class="s-">concurrent insert</span> → page rest',
           'assert every item appears <span class="o-">exactly once</span>',
           '',
           '<span class="c-"># the mutant (authored eval-blind)</span>',
           '- <span class="o-">keyset cursor on (created_at, id)</span>',
           '+ <span class="m-">ORDER BY created_at LIMIT / OFFSET</span>'], filetag='evals/session.py  +  evals/mutant.diff')}
    <div class="codecap">A vacuous eval (<span class="bad">assert True</span>) is green-on-right — but green-on-wrong too. So it is <b>rejected</b>.</div>
  </div>
  <div class="stack">
    {truth([("unit test","PASS","PASS"),("the eval","PASS","FAIL")])}
    {card("Kill record","RED-on-mutant is the proof","The mutant the eval catches IS its evidence of specificity. Recorded in trust.log; invalidated when the eval or intent changes (drift → re-verify).","")}
  </div>
</div>""")
slide(kind="content", eyebrow="Anti-collusion", title="The information barrier", body=f"""
<div class="grid g2" style="gap:22px">
  <div class="card" style="border-color:color-mix(in srgb,var(--pass) 30%,var(--line))">
    <div class="k" style="color:var(--pass)">The mutant author SEES</div>
    <ul class="bul sm" style="margin-top:12px">
      <li>The <b>intent</b> (plain prose)</li>
      <li>The <b>code under test</b></li>
    </ul>
    <p class="mut" style="margin-top:12px;font-size:14.5px">…and must write a plausible diff that violates the intent.</p>
  </div>
  <div class="card" style="border-color:color-mix(in srgb,var(--fail) 30%,var(--line))">
    <div class="k" style="color:var(--fail)">The mutant author NEVER sees</div>
    <ul class="bul sm" style="margin-top:12px">
      <li>The <b>eval</b> it must beat</li>
    </ul>
    <p class="mut" style="margin-top:12px;font-size:14.5px">Blind to the assertion, it can’t craft a <b>strawman</b> tuned to be caught. In Tier 2 this is an <b>eval-blind git worktree</b>.</p>
  </div>
</div>
<div class="note" style="margin-top:18px">Gold standard: a <b>surgical</b> mutant that breaks one intent facet while every <b>other</b> eval stays green — proof the eval is load-bearing and non-redundant.</div>""")
slide(kind="content", eyebrow="Coverage validity", title="The bounded intent-audit", body=f"""
<div class="grid g21" style="gap:28px">
  <div class="stack">
    <div class="lead">An independent auditor sees <b>only the intent + the eval set</b> — never the code — and must <b>exhibit a betrayer</b>: an implementation that passes every eval yet violates a named facet.</div>
    <div class="note">It answers the question trust alone can’t: <i>is anything intended but un-evaluated?</i></div>
  </div>
  <div class="stack">
    <div class="row"><span class="dot" style="background:var(--fail)"></span><b>Betrayer found</b> <span class="mut">→ required new eval</span></div>
    <div class="row"><span class="dot" style="background:var(--pass)"></span><b>2 clean rounds</b> <span class="mut">→ satisfied</span></div>
    <div class="row"><span class="dot" style="background:var(--warn)"></span><b>3-round cap</b> <span class="mut">→ escalate, never spin</span></div>
  </div>
</div>""")
slide(kind="content", eyebrow="State model", title='Every fact is <span class="hl">PRIMITIVE</span> or <span class="hl">DERIVED</span>', body=f"""
<div class="grid g2" style="gap:22px">
  {card("Primitive — authored once","Written, never recomputed","objective · spec · spec.lock · tasks · trust.log · runs.log · decisions. Append-only where it counts, so a torn write is the worst damage.","")}
  {card("Derived — pure f(disk)","Computed at read time, never stored","phase · coverage · eval-trust · the next action · the handoff dossier. Nothing to corrupt, nothing to go stale, no dual source of truth.","")}
</div>
<div class="note" style="margin-top:18px">This is what makes “the next action is a pure function of disk” <b>literally true</b> — and why a fresh agent always agrees with the last one.</div>""")
slide(kind="content", eyebrow="The state machine", title="The ladder — resume is derivation", body=f"""
<div class="grid g21" style="gap:26px;align-items:center">
  <div class="ladder">
    <div class="rung done"><span class="num">0</span><span class="ph">spec</span><span class="gd">≥1 intent line</span></div>
    <div class="rung done"><span class="num">1</span><span class="ph">bind</span><span class="gd">every intent has an eval</span></div>
    <div class="rung on"><span class="num">2</span><span class="ph">trust</span><span class="gd">killed ∧ passed @ current hash</span></div>
    <div class="rung"><span class="num">3</span><span class="ph">freeze</span><span class="gd">spec.lock == spec (diff)</span></div>
    <div class="rung"><span class="num">4</span><span class="ph">execute</span><span class="gd">ready tasks done</span></div>
    <div class="rung"><span class="num">5</span><span class="ph">eval-run</span><span class="gd">required verdicts PASS</span></div>
    <div class="rung"><span class="num">6</span><span class="ph">done</span><span class="gd">no drift</span></div>
  </div>
  <div class="stack">
    <div class="lead" style="font-size:19px">The <b>first failing rung</b> is the phase; its action is the next action.</div>
    <div class="note">The resume protocol and the deterministic deriver walk the <b>same</b> ladder — so they can never diverge.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="Context-rot defense", title="Hand off before rot — proven, not promised", body=f"""
<div class="grid g3" style="gap:18px">
  <div class="card tight"><div class="kpi ac">2</div><div class="kpi-l">cold agents recovered objective + next action + eval status from <b>disk alone</b></div></div>
  <div class="card tight"><div class="kpi ok">0</div><div class="kpi-l">chat history needed — the repo is the memory, the session is a cache</div></div>
  <div class="card tight"><div class="kpi">rung&nbsp;2</div><div class="kpi-l">trust evaluated <b>by hand</b> from RESUME.md; matched the deriver exactly</div></div>
</div>
<div class="note" style="margin-top:18px">No token-fraction guesswork. Every step ends at a <b>committed, clean boundary</b>, so handing off “too early” costs only one cheap re-derivation. A stale handoff is detected by its git fingerprint and ignored.</div>""")
slide(kind="content", eyebrow="Adoptability", title="One framework, three tiers", body=f"""
<div class="grid g3">
  <div class="card tier"><div class="k">Tier 0</div><h3>Discipline</h3><p>Plain files; your own runner. The filesystem layout <b>is</b> the state machine. Minutes to adopt, no runtime.</p><div class="bar"><i style="width:34%"></i></div></div>
  <div class="card tier"><div class="k">Tier 1</div><h3>Gated</h3><p>Eval-trust + coverage + the ladder, enforced by 8 slash-command skills and a tested read-only deriver.</p><div class="bar"><i style="width:67%"></i></div></div>
  <div class="card tier"><div class="k">Tier 2</div><h3>Factory</h3><p>Bounded autonomous loop — fresh context per rung, caps, escalation, kill-switch. The software factory.</p><div class="bar"><i style="width:100%"></i></div></div>
</div>""")
slide(kind="content", eyebrow="Roles", title="Operator’s-eye view: who does what", body=f"""
<div class="grid g2" style="gap:22px">
  <div class="card"><div class="k" style="color:var(--accent)">The human decides</div>
    <ul class="bul sm" style="margin-top:12px">
      <li>The <b>objective</b> and how to slice it</li>
      <li>Ambiguous intent (auth, money, ordering)</li>
      <li>“Done when” — the factory escalates, never self-declares</li>
      <li>When to arm the kill-switch / steer</li>
    </ul></div>
  <div class="card"><div class="k" style="color:var(--accent2)">The agent / factory does</div>
    <ul class="bul sm" style="margin-top:12px">
      <li>Draft specs, write evals, author eval-blind mutants</li>
      <li>Implement slices; run the suite; write verdicts</li>
      <li>Derive the next action; hand off cleanly</li>
      <li>Stop at every committed boundary</li>
    </ul></div>
</div>""")

# USING IT
slide(kind="content", eyebrow="Using it · the verbs", title="Eight slash commands, one ladder", body=f"""
<div class="grid g4" style="gap:13px">
  {card("/sde-init","scaffold","Create .sde/, capture the objective.","tight")}
  {card("/sde-spec","intents","Author the slice’s intent statements.","tight")}
  {card("/sde-eval","trust ★","Bind evals + the eval-blind mutant barrier.","tight")}
  {card("/sde-next","drive","Do the one derived action, then checkpoint.","tight")}
  {card("/sde-verify","gate","Run the suite + the intent-audit.","tight")}
  {card("/sde-handoff","freeze","Stamp the dossier for a clean resume.","tight")}
  {card("/sde-resume","cold start","Recover state from disk, continue.","tight")}
  {card("/sde-status","read","Derived phase, coverage, trust, next.","tight")}
</div>
<div class="note" style="margin-top:16px">Each is a thin layer over the on-disk state + the deriver, so they can’t drift from each other. <span class="cmd" style="padding:1px 7px">/sde-factory</span> wraps <span class="cmd" style="padding:1px 7px">/sde-next</span> for Tier 2.</div>""")
slide(kind="content", eyebrow="Using it · quick start", title="From zero to a gated slice", body=f"""
<div class="grid g2" style="gap:22px">
  {code(['<span class="c-"># Tier 0 — no install</span>',
         'cp -r framework/templates/.sde ./.sde',
         '<span class="c-"># edit objective.md + slices/01-*/spec.md</span>',
         '<span class="c-"># write evals + a mutant diff per intent</span>',
         '<span class="c-"># run them with YOUR runner; follow RESUME.md</span>'], filetag='Tier 0 · pure convention')}
  {code(['<span class="c-"># Tier 1 — Claude Code skills</span>',
         '<span class="k-">/sde-init</span> "page the list, every item once"',
         '<span class="k-">/sde-spec</span>  →  <span class="k-">/sde-eval</span>  →  <span class="k-">/sde-next</span>',
         '<span class="k-">/sde-verify</span>',
         '<span class="k-">/sde-resume</span>      <span class="c-"># after any context reset</span>'], filetag='Tier 1 · gated')}
</div>
<div class="note" style="margin-top:16px">Any step may run in a fresh session. <span class="cmd" style="padding:1px 7px">/sde-resume</span> continues from the derived next action.</div>""")
slide(kind="content", eyebrow="Using it · on disk", title="The repository is the memory", body=f"""
<div class="grid g21" style="gap:28px">
  {code(['.sde/',
         '├─ objective.md        <span class="c-"># north star + “done when”</span>',
         '├─ decisions.md        <span class="c-"># append-only ADRs</span>',
         '├─ RESUME.md           <span class="c-"># the ladder (run by hand or sde)</span>',
         '├─ runs.log            <span class="c-"># append-only verdicts</span>',
         '└─ slices/01-…/',
         '   ├─ spec.md  spec.lock.md',
         '   ├─ tasks.md  trust.log',
         '   └─ evals/'], filetag='project/.sde')}
  <div class="stack">
    {card("Greppable, catable","No black box","Read the whole state with cat. The deriver only reads it; it stores nothing.","")}
    <div class="note">App code lives in your normal tree (<span class="cmd" style="padding:1px 7px">src/</span>, <span class="cmd" style="padding:1px 7px">evals/</span>). <b>.sde/</b> holds state, not code.</div>
  </div>
</div>""")

# FACTORY
slide(kind="content", eyebrow="Tier 2 · the factory", title="A mechanical loop, fresh context per rung", body=f"""
<div class="grid g12" style="gap:26px">
  {code(['<span class="k-">while</span> sde next; <span class="k-">do</span>',
         '  rc=$?                       <span class="c-"># 0 done · 2 work · 1 error</span>',
         '  [ $rc = 0 ] &amp;&amp; <span class="m-">escalate</span> done-when   <span class="c-"># never auto-succeed</span>',
         '  before=$(git rev-parse HEAD)',
         '  <span class="k-">claude -p</span> "do ONLY the next action; commit; stop"',
         '  [ HEAD = before ] &amp;&amp; <span class="m-">escalate</span> no-progress',
         '<span class="k-">done</span>'], filetag='framework/bin/sde-factory.sh')}
  <div class="stack">
    {card("Executor in the harness","Agents propose; the driver decides","Only the driver runs evals/mutants and writes the logs — a builder can’t grade its own work.","")}
    {card("No session rots","One rung = one fresh claude -p","Nothing lives long enough to decay; the loop is the durable part, not the session.","")}
  </div>
</div>""")
slide(kind="content", eyebrow="Tier 2 · safety", title="Bounded autonomy — designed to halt", body=f"""
<div class="grid g3" style="gap:16px">
  {card("Hard stops","Caps everywhere","HEAD-based no-progress retry cap + a single MAX_STEPS budget + a .sde/STOP kill-switch + a steer file.","tight")}
  {card("Never weaken a gate","Escalate, don’t cheat","A gate that won’t pass after N tries blocks + escalates. The loop never lowers a bar to get green.","tight")}
  {card("Structural guards","Cheating can’t pay","Weakening an eval re-opens its trust; forged verdicts can’t (driver writes them); a vacuous eval can never reach done.","tight")}
</div>
<div class="note" style="margin-top:18px">The driver <b>commits to a branch and never pushes or deploys</b>. Humans own “done.”</div>""")

# EXAMPLE 1 — SaaS
slide(kind="section", big="01", title="Example 1 — Multi-tenant SaaS",
      badges='<span class="badge be">Web + API</span><span class="badge illus">Illustrative walkthrough</span>',
      sub="A team project tracker. The intent that ordinary tests miss: a user must never see another organization’s data.")
slide(kind="content", eyebrow="Example 1 · scope", title="One objective, four slices", badges='<span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g21" style="gap:28px">
  {card("Objective","Ship a multi-tenant tracker","Organizations sign up, invite teammates, and manage projects — each org’s data fully isolated from every other.","")}
  <div class="stack">
    <div class="row"><span class="num">01</span><b>Auth &amp; org membership</b></div>
    <div class="row"><span class="num">02</span><b>Projects list</b> <span class="mut">— tenant isolation ★</span></div>
    <div class="row"><span class="num">03</span><b>Invite teammates</b> <span class="mut">— roles</span></div>
    <div class="row"><span class="num">04</span><b>Billing</b> <span class="mut">— subscription</span></div>
  </div>
</div>""")
slide(kind="content", eyebrow="Example 1 · slice 02 · spec", title="The intent the tests forget", badges='<span class="badge be">Web + API</span><span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g12" style="gap:28px">
  {code(['I1. A user only ever sees projects that',
         '    belong to <span class="o-">their own organization</span>.',
         '    eval: contract  evals/isolation.py',
         '          gate=<span class="k-">required</span>  mutant=evals/leak.diff',
         '',
         'I2. Members see all org projects; the org',
         '    boundary is never crossed by a filter,',
         '    a search, or a direct id lookup.'], filetag='.sde/slices/02-projects/spec.md')}
  <div class="stack">
    {card("Why it’s dangerous","Silent, not loud","A tenant leak doesn’t crash. It returns data — the wrong org’s. Nothing in a single-tenant test suite notices.","")}
    <div class="note">The intent is a <b>negative</b> (“never sees…”). Negatives are exactly what example-based tests under-cover.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="Example 1 · slice 02 · eval", title="The eval seeds two tenants", badges='<span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g12" style="gap:28px">
  <div class="stack">
    {code(['<span class="c-"># the mutant: forgets the tenant filter</span>',
           '- WHERE owner_id=? <span class="o-">AND org_id=?</span>',
           '+ WHERE owner_id=?            <span class="m-"># leaks</span>',
           '',
           '<span class="c-"># the eval: seed org A + org B</span>',
           'login as a member of <span class="s-">org A</span>',
           'GET /projects → assert <span class="o-">0 rows</span> from org B'], filetag='src/projects.sql  +  evals/isolation.py')}
    <div class="codecap">The unit test seeds <b>one</b> org, so both impls return the same rows — green.</div>
  </div>
  <div class="stack">
    {truth([("unit test · 1 org","PASS","PASS"),("isolation eval · 2 orgs","PASS","FAIL")], head=("with filter","without"))}
    <div class="note illus"><b>Illustrative.</b> The mutant (a dropped <span class="cmd" style="padding:1px 7px">AND org_id=?</span>) is the textbook multi-tenant leak.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="Example 1 · slice 02 · drive", title="Trust → freeze → execute", badges='<span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g2" style="gap:22px">
  <div class="ladder">
    <div class="rung done"><span class="num">✓</span><span class="ph">bind</span><span class="gd">isolation.py bound to I1</span></div>
    <div class="rung done"><span class="num">✓</span><span class="ph">trust</span><span class="gd">leak.diff killed it · barrier on</span></div>
    <div class="rung done"><span class="num">✓</span><span class="ph">freeze</span><span class="gd">spec locked</span></div>
    <div class="rung on"><span class="num">→</span><span class="ph">execute</span><span class="gd">implement the scoped query</span></div>
  </div>
  <div class="stack">
    {card("Order matters","Eval before code","The eval is trusted — and red — before the query is written. The first job of the executor is to turn it green the right way.","")}
    <div class="note">Each rung ends in a commit. If context fills here, a fresh <span class="cmd" style="padding:1px 7px">/sde-resume</span> picks up at <b>execute</b>.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="Example 1 · outcome", title="The leak is caught before it ships", badges='<span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g21" style="gap:26px;align-items:center">
  <div class="stack">
    <div class="lead">Implementation lands. <span class="cmd" style="padding:1px 7px">/sde-verify</span> runs the suite: the isolation eval goes <b class="ok">green</b>; the intent-audit finds no betrayer. Slice 02 derives <b>done</b>.</div>
    <div class="note">A regression that drops the filter later → eval red → the gate blocks the merge. The intent is now permanently guarded.</div>
  </div>
  <div class="card tight"><div class="k">What the eval bought</div>
    <p style="margin-top:8px;font-size:15px">A <b>negative intent</b> (“never another org’s data”) turned into an executable, regression-proof guard — the one the unit suite structurally couldn’t express.</p></div>
</div>""")

# EXAMPLE 2 — Payment gateway
slide(kind="section", big="02", title="Example 2 — Payment gateway",
      badges='<span class="badge be">Backend</span><span class="badge mob">Merchant mobile app</span><span class="badge adm">Admin dashboard</span><span class="badge illus">Illustrative walkthrough</span>',
      sub="One objective spanning three surfaces. Each surface has an intent that is cheap to get wrong and expensive to ship wrong.")
slide(kind="content", eyebrow="Example 2 · scope", title="Three surfaces, one objective", badges='<span class="badge illus">Illustrative</span>', body=f"""
<div class="stack" style="gap:14px">
  <div class="surf"><span class="badge be">Backend</span><div><b>Idempotent charges</b> · money rounding · webhooks <span class="mut">— the ledger of record</span></div></div>
  <div class="surf"><span class="badge mob">Mobile</span><div><b>Merchant checkout</b> · never show “Paid” before the gateway confirms <span class="mut">— Maestro journey</span></div></div>
  <div class="surf"><span class="badge adm">Admin</span><div><b>Payouts &amp; reconciliation</b> · only finance-role may move money <span class="mut">— RBAC</span></div></div>
  <div class="note" style="margin-top:6px">Slices are <b>vertical</b>: each spans the surface end-to-end and carries its own trusted evals. The factory runs them with disjoint write sets.</div>
</div>""")
slide(kind="content", eyebrow="Example 2 · backend · intent", title="The same payment, submitted twice", badges='<span class="badge be">Backend</span><span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g21" style="gap:28px">
  {card("Intent I1","Charge exactly once","A retry, a flaky network, a double-tap — submitting the same payment twice must bill the customer once, and return the same charge.","")}
  <div class="stack">
    <div class="lead" style="font-size:19px">This is the single most expensive bug class in payments — and the easiest to pass a happy-path test.</div>
    <div class="note">The contract is the <b>idempotency key</b>: same key in, same charge out, no second row.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="Example 2 · backend · eval", title="The eval replays the key", badges='<span class="badge be">Backend</span><span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g12" style="gap:28px">
  <div class="stack">
    {code(['POST /charges   Idempotency-Key: <span class="s-">abc</span>',
           '',
           '<span class="c-"># mutant — ignores the key</span>',
           'charge = create(amount)        <span class="m-"># → 2 rows</span>',
           '<span class="c-"># right — atomic upsert on the key</span>',
           'charge = <span class="o-">get_or_create(key, amount)</span>'], filetag='src/charges.py')}
    <div class="codecap">The unit test sends <b>one</b> request. The intent is about the <b>second</b>.</div>
  </div>
  <div class="stack">
    {truth([("unit · 1 request","PASS","PASS"),("eval · 2× same key","PASS","FAIL")])}
    {card("What the eval asserts","One charge, same id","Two requests, identical key → exactly one row, and the same charge id returned both times.","")}
  </div>
</div>""")
slide(kind="content", eyebrow="Example 2 · mobile · journey", title="Never show “Paid” before the gateway confirms", badges='<span class="badge mob">Mobile</span><span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g12" style="gap:28px">
  <div class="stack">
    {code(['appId: com.paybridge.merchant',
           '- launchApp',
           '- tapOn: "Charge $20"',
           '<span class="c-"># mutant: optimistic UI marks Paid on tap</span>',
           '- assertVisible: <span class="o-">"Declined"</span>   <span class="c-"># test card</span>',
           '- assertNotVisible: <span class="m-">"Paid"</span>'], filetag='evals/checkout.maestro.yaml')}
    <div class="note illus"><b>Documented contract, not a device run.</b> The runner-agnostic journey (<i>flow → {{verdict, artifacts}}</i>) has an executable API-level analogue.</div>
  </div>
  <div class="stack">
    {truth([("unit · render receipt","PASS","PASS"),("journey · decline","PASS","FAIL")], head=("confirm-first","optimistic"))}
    {card("The intent","Truth over optimism","A declined card must read “Declined.” Showing “Paid” before settlement is the violation the journey eval pins.","")}
  </div>
</div>""")
slide(kind="content", eyebrow="Example 2 · admin · RBAC", title="Only finance-role can move money", badges='<span class="badge adm">Admin</span><span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g12" style="gap:28px">
  <div class="stack">
    {code(['<span class="c-"># mutant: missing the role check</span>',
           'POST /payouts → create_payout()  <span class="m-"># any admin</span>',
           '<span class="c-"># right: guard the endpoint</span>',
           '<span class="o-">require_role("finance")</span>',
           '',
           '<span class="c-"># the eval: an authz matrix</span>',
           'as <span class="s-">ops</span>     → expect <span class="o-">403</span>',
           'as <span class="s-">finance</span> → expect <span class="o-">200</span>'], filetag='src/payouts.py  +  evals/authz.py')}
  </div>
  <div class="stack">
    {truth([("unit · finance pays","PASS","PASS"),("authz · ops blocked","PASS","FAIL")])}
    <div class="note illus"><b>Illustrative.</b> A missing role check passes every “happy path” test — finance can still pay out. Only the <b>negative</b> case (ops must be blocked) catches it.</div>
  </div>
</div>""")
slide(kind="content", eyebrow="Example 2 · the factory", title="One loop drives all three surfaces", badges='<span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g21" style="gap:26px">
  <div class="stack">
    <div class="flow">
      <span class="pill"><span class="dot" style="background:var(--accent)"></span>backend</span><span class="arr">·</span>
      <span class="pill"><span class="dot" style="background:var(--accent2)"></span>mobile</span><span class="arr">·</span>
      <span class="pill"><span class="dot" style="background:var(--warn)"></span>admin</span>
    </div>
    <div class="note">Disjoint slice directories → the factory advances them with no write contention. Each rung is a fresh, information-scoped <span class="cmd" style="padding:1px 7px">claude -p</span>; mutants are authored in an eval-blind worktree; a different-model judge grades the “clear error message” semantic eval at rungs 2 and 5.</div>
  </div>
  <div class="card tight"><div class="k">When a gate won’t pass</div>
    <p style="margin-top:8px;font-size:15px">The slice is <b>blocked + escalated</b> to the human queue — the loop moves to an independent slice or stops. It never weakens the idempotency eval to go green.</p></div>
</div>""")
slide(kind="content", eyebrow="Example 2 · recap", title="Three surfaces, three intent violations caught", badges='<span class="badge illus">Illustrative</span>', body=f"""
<div class="grid g3">
  {card("Backend","Double charge","An idempotency-blind handler billed twice on a retry — green on the 1-request test, red on the replay eval.","tight")}
  {card("Mobile","Optimistic “Paid”","The app showed success before settlement — green on the receipt test, red on the decline journey.","tight")}
  {card("Admin","Missing authz","A payout endpoint any admin could call — green on the finance happy-path, red on the ops-blocked matrix.","tight")}
</div>
<div class="note" style="margin-top:18px">Each is a <b>negative or second-order</b> intent — the exact shape ordinary tests under-cover, and exactly what a trusted eval pins.</div>""")

# CLOSE
slide(kind="content", eyebrow="Honesty", title="What is proven vs. designed", body=f"""
<div class="grid g2" style="gap:22px">
  <div class="card" style="border-color:color-mix(in srgb,var(--pass) 28%,var(--line))">
    <div class="k" style="color:var(--pass)">Proven · runs in the repo</div>
    <ul class="bul sm" style="margin-top:12px">
      <li>Eval-trust on real code (pagination): mutant green on tests, red on eval</li>
      <li>The deriver is tested (6/6); resumability shown by two cold agents</li>
      <li>The framework dogfoods itself — state resumes from disk</li>
    </ul></div>
  <div class="card" style="border-color:color-mix(in srgb,var(--warn) 28%,var(--line))">
    <div class="k" style="color:var(--warn)">Designed · not yet run here</div>
    <ul class="bul sm" style="margin-top:12px">
      <li>The Tier-2 factory’s unattended run (driver written, not executed)</li>
      <li>A real mobile device journey; a live different-model judge</li>
      <li><b>The two examples are illustrative</b> walkthroughs of the method</li>
    </ul></div>
</div>""")
slide(kind="content", eyebrow="Where to start", title="Read it, run the proof, slice your objective", body=f"""
<div class="grid g21" style="gap:28px">
  <div class="stack">
    {code(['<span class="c-"># see an eval catch an intent violation</span>',
           'bash examples/01-pagination/run.sh',
           '',
           '<span class="c-"># watch the framework derive its own state</span>',
           'python3 framework/bin/sde status --root .'], filetag='start here')}
    <div class="row wrap" style="gap:8px"><span class="badge">FRAMEWORK.md</span><span class="badge">examples/01-pagination</span><span class="badge">docs/reasoning/00–04</span></div>
  </div>
  <div class="stack" style="justify-content:center">
    <div class="lead" style="font-size:21px">Code generation was never the hard part. <b>Knowing it built what you meant</b> is — and the eval is what knows.</div>
  </div>
</div>""")


# ── rendering ────────────────────────────────────────────────────────────────
def render_slide(s, i, total):
    pg = (f'<footer class="s-foot"><span class="brand">SDE · Spec-Driven, Evals-First</span>'
          f'<span class="pg">{i:02d} / {total:02d}</span></footer>')
    if s["kind"] == "cover":
        inner = f"""<div class="slide-in cover">
          <div class="kick">Spec-Driven Development · Evals-First</div>
          <h1>SDE<span class="e">.</span></h1>
          <div class="tag">Build full-stack &amp; mobile software where <b>evals confirm the code follows
            the intent</b> — not just that it runs. With autonomous handoff and a path to a self-running
            software factory.</div>
          <div class="meta"><span class="badge">How it works</span><span class="badge be">Example 1 · SaaS</span>
            <span class="badge mob">Example 2 · Payment gateway</span></div>
        </div>{pg}"""
    elif s["kind"] == "statement":
        inner = f"""<div class="slide-in"><div class="statement"><div class="q">{s['q']}</div>
          <div class="by">— {s['by']}</div></div></div>{pg}"""
    elif s["kind"] == "section":
        badges = f'<div class="badges">{s["badges"]}</div>' if s.get("badges") else ""
        inner = f"""<div class="slide-in sec" style="justify-content:center">
          <div class="big">{s['big']}</div><h2>{s['title']}</h2>{badges}<p>{s.get('sub','')}</p></div>{pg}"""
    else:
        badges = f'<div class="badges">{s["badges"]}</div>' if s.get("badges") else ""
        head = (f'<div class="head-row"><div><div class="eyebrow">{s["eyebrow"]}</div>'
                f'<h2 class="s-title">{s["title"]}</h2></div>{badges}</div>')
        inner = f'<div class="slide-in">{head}<div class="s-body">{s["body"]}</div></div>{pg}'
    return f'<section class="slide" data-i="{i}">{inner}</section>'

def render_doc(theme_name):
    t = THEMES[theme_name]
    root = ":root{" + "".join(f"--{k}:{v};" for k, v in t.items()) + "}"
    total = len(SLIDES)
    slides_html = "\n".join(render_slide(s, i + 1, total) for i, s in enumerate(SLIDES))
    extra = (PRINT_CSS if theme_name == "print" else "") + (DEBUG_CSS if DEBUG else "")
    nav = "" if theme_name == "print" else """
<script>
const S=[...document.querySelectorAll('.slide')];let i=0;
function go(n){i=Math.max(0,Math.min(S.length-1,n));S[i].scrollIntoView({behavior:'smooth'})}
addEventListener('keydown',e=>{if(['ArrowRight','ArrowDown',' ','PageDown'].includes(e.key)){e.preventDefault();go(i+1)}
if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();go(i-1)}
if(e.key==='Home')go(0);if(e.key==='End')go(S.length-1)});
const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting)i=S.indexOf(x.target)}),{threshold:.6});
S.forEach(s=>io.observe(s));
</script>"""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SDE — Spec-Driven, Evals-First ({theme_name})</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;450;600;700;750;800;850&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{root}{BASE_CSS}{extra}</style></head>
<body><div class="deck">{slides_html}</div>{nav}</body></html>"""

def main():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    out = {"dark": "sde-presentation-dark.html", "light": "sde-presentation-light.html",
           "print": "sde-presentation-print.html"}
    for theme, fn in out.items():
        path = os.path.join(here, ("_debug-" if DEBUG else "") + fn)
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_doc(theme))
        print(("[debug] " if DEBUG else "") + f"wrote {path}  ({len(SLIDES)} slides)")

if __name__ == "__main__":
    main()
