# SDE — Presentation

A 35-slide deck explaining how SDE works, how to use it, and two end-to-end walkthroughs
(a multi-tenant SaaS and a payment gateway with a merchant mobile app, backend, and admin dashboard).

## The three versions
| File | For |
|---|---|
| `sde-presentation-dark.html` | on-screen presenting (dark theme) |
| `sde-presentation-light.html` | on-screen presenting (light theme) |
| `sde-presentation-print.html` | **printing / PDF** — white background, one slide per page, no dark fills |

Open any file in a browser. **Navigate** with `→ / ← / Space / PageUp / PageDown / Home / End`.
To make a PDF: open the **print** file and use the browser's Print → *Save as PDF* (it paginates one
slide per A-wide landscape page). All three share identical content and layout — only the theme differs.

## How it's built
One generator, one content source → three themed files (so content can never drift between themes):
```bash
python3 build.py            # writes the 3 final HTML files
python3 build.py --debug    # writes _debug-*.html with content-box outlines + overflow visible
                            # (used to verify no slide overflows before shipping)
```
Edit slides in the `SLIDES` list in `build.py`; themes live in `THEMES`. No build step or
dependencies beyond Python 3 — the fonts (Inter, JetBrains Mono) load from Google Fonts.

## Slide map
1. **Intro** — the thesis: tests prove it runs; evals prove it followed intent.
2. **How it works** — lifecycle · spec = intents · GREEN-on-right ∧ RED-on-wrong · the information
   barrier · intent-audit · PRIMITIVE/DERIVED · the ladder · resumability · the three tiers · roles.
3. **Using it** — the eight slash commands · quick start · the `.sde/` layout.
4. **The factory** — the mechanical Tier-2 driver · bounded autonomy.
5. **Example 1 — multi-tenant SaaS** — a tenant-isolation slice, end to end.
6. **Example 2 — payment gateway** — backend idempotency, a mobile checkout journey, and admin RBAC.
7. **Close** — proven vs. designed (honest) · where to start.

## Honesty note
The two examples are **illustrative walkthroughs of the method** (badged as such on every example
slide). Only the pagination example is actually executed in this repo — see
[`../KNOWN-LIMITATIONS.md`](../KNOWN-LIMITATIONS.md). The deck's "proven vs. designed" slide states
this plainly so the polish never outruns the truth.
