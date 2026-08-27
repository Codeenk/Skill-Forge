# Skill-Forge

> **Meta-skill that compiles installed skills into portable team skills.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](scripts/forge.py)
[![Agent Skills Spec](https://img.shields.io/badge/spec-Agent%20Skills-green.svg)](https://github.com/anthropics/skills)

Not an agent framework. Not generated Python agents. **Skill-Forge takes your already-installed `SKILL.md` files as raw material and emits one portable `SKILL.md` bundle** that orchestrates them through phased filesystem handoffs — runnable on any Agent Skills-compatible runtime (Claude Code, OpenCode, Cursor, Codex, Gemini CLI, Command Code, Goose, Amp, Roo Code, Kiro, TRAE, Copilot, Factory Droid, Windsurf, Junie, ...).

---

## Why Skill-Forge

| Problem | Skill-Forge Fix |
|---|---|
| Mega-prompts inlined (2k+ lines) | **Progressive disclosure** — `Read first: ~/path/to/SKILL.md` per phase, bundle <500 lines |
| Chat history as state | **Filesystem as state machine** — `/.team/artifacts/*` handoffs |
| Works only on Claude | **No runtime-proprietary language** — every runtime can read files |
| Overwrites non-existent dirs | **Detection-first install** — writes only to existing `*/skills` roots |
| Hand-edited hashes | **Determinism split** — scripts hash, you judge |

---

## Quick Start

Install the forge bundle into any runtime:

```bash
npx skills add skill-forge
# or
cp -r skill-forge ~/.agents/skills/
cp -r skill-forge ~/.config/opencode/skills/
```

Then in your agent:

> *“forge me a full-stack team for Next.js + Postgres + Auth”*

### Direct CLI

```bash
# 1. Discover everything installed everywhere
python3 scripts/forge.py scan --out .team/manifest.json
# → 325 skills across 3 roots

# 2. After synthesis, validate
python3 scripts/forge.py lint ./my-team

# 3. Install to every detected runtime
python3 scripts/forge.py install ./my-team

# 4. Later: check drift
python3 scripts/forge.py verify ./my-team
# OK / MISSING / DRIFTED per roster member
```

---

## How It Works — 5 Gates

**Gate 0 — Understand intent** — Ask at most once: `team name`, `purpose`, `stack constraints`, `exclusions`. Derive `<domain>-team` if no name.

**Gate 1 — Discover** — `scan` walks `PROJECT_ROOTS` + `HOME_ROOTS` (11 patterns + `FORGE_EXTRA_ROOTS`), dedupes by realpath, hashes `sha256:16hex`, writes `skill-forge/manifest@1` JSON.

**Gate 2 — Select roster** — From manifest ONLY. Never hallucinate. 2–8 members, declare gaps aloud: `no testing skill found - proceeding without coverage`.

**Gate 3 — Synthesize** — Fill `templates/team-skeleton.md` per `references/synthesis-protocol.md` (topology → owner binding → contracts → assemble → sidecar). Frontmatter `name==dirname`, `description` ≤1024 chars with `Use when...`, artifact names unique, inputs only from earlier phases. Copy `scripts/forge.py` self-contained + write `.forge/manifest.json` provenance sidecar.

**Gate 4 — Validate** — `lint` enforces `team-schema.md`: name regex, description triggers, allowed frontmatter only, phase numbering `1..N`, artifact dependency order, sidecar existence.

**Gate 5 — Install everywhere** — Mirrors bundle to every existing `*/skills` root (`--into` for explicit, `--force` to overwrite).

---

## Generated Team Contract

```
my-team/
├── SKILL.md              # <500 lines, phased workflow
├── .forge/manifest.json  # {roster:[{skill,path,hash}], generated_at, source_workspace}
└── scripts/forge.py      # stdlib-only, self-contained
```

Body order: `Title → How this runs → Operating rules (5 bullets) → Team roster table → Phase workflow (### Phase N: blocks) → Completion report`.

Phase block:

```md
### Phase N: kebab-title
Owner: `skill-name`
Read first: `~/path/to/SKILL.md`
Objective: one verifiable sentence
Inputs: `.team/artifacts/x.json` (Phase M) or `(none)`
Actions: 1. Apply owner method... 2. Produce Outputs...
Outputs: `.team/artifacts/name.ext` - shape: JSON keys / md sections
Exit: Artifact exists, parses, contains keys...
Fallback: On missing inputs... produce best-effort, mark deviation...
```

---

## Layout

```
skill-forge/
├── SKILL.md                         # install this
├── references/
│   ├── synthesis-protocol.md        # Steps A-E: topology → bind → contracts → assemble
│   ├── team-schema.md               # lint contract (frontmatter, body, phase, sidecar)
│   └── runtime-paths.md             # 11 roots + detection policy
├── templates/
│   ├── team-skeleton.md             # frontmatter + 5 operating rules + roster + phases
│   └── phase-contract.md            # per-phase block template
├── scripts/forge.py                 # scan | lint | install | verify (376 lines, stdlib only)
└── examples/
    └── design-review-team/          # golden reference compiled team
```

---

## Examples

| Team | Roster | Use when |
|---|---|---|
| `fullstack-dev-team` | nextjs, tailwind, postgres, nodejs, auth, e2e | *build a full-stack app end to end* |
| `design-review-team` | ui-ux-pro-max, accessibility, brand | *review a design before shipping* |

---

## Development

```bash
python3 scripts/forge.py lint ./skill-forge
python3 scripts/forge.py verify ./skill-forge
```

Requires Python 3.9+, no deps beyond stdlib.

---

## License

MIT — see [LICENSE](LICENSE).

## Author

Built by [Codeenk](https://github.com/Codeenk) — [malandkar.sarvesh@gmail.com](mailto:malandkar.sarvesh@gmail.com)
