# Skill-Forge

> **Meta-skill that compiles installed skills into portable team skills.**

[![Release](https://img.shields.io/github/v/release/Codeenk/Skill-Forge?color=blue&logo=github)](https://github.com/Codeenk/Skill-Forge/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Spec: Agent Skills](https://img.shields.io/badge/Spec-agentskills.io-emerald)](https://agentskills.io)
[![Zero Dependency](https://img.shields.io/badge/Dependencies-Stdlib%20Only-brightgreen)](#)
[![Security: AST Audited](https://img.shields.io/badge/Security-AST%20Audited-green?logo=securityscorecard)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Codeenk/Skill-Forge/pulls)

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

**Gate 1 — Discover** — `scan` walks `PROJECT_ROOTS` + `HOME_ROOTS` (11 patterns + `FORGE_EXTRA_ROOTS`), dedupes by realpath, hashes `sha256:16hex` (+ `git SHA`), writes `skill-forge/manifest@1` JSON. `.forge/vendor` is always scanned (hermetic vendor).

**Gate 1.5 — Resolve (cold-start)** — If Gate 1 missing a capability (e.g., `stripe-billing`), auto-research via curated `references/registries.json` (`npx skills find` → agentskills.io + GitHub `#agent-skills` + allowlist), sandbox to `/tmp/forge-incoming/`, `audit PASS` required, then vendor-scoped to `.forge/vendor/<skill>` (default, hermetic) or `--global` with explicit consent. `--offline` disables fetch for air-gapped CI.
```bash
python3 scripts/forge.py resolve --need stripe-billing --out .forge/vendor
python3 scripts/forge.py resolve --need stripe-billing --global   # global with consent
python3 scripts/forge.py resolve --need stripe-billing --offline   # enterprise CI
```

**Gate 2 — Select roster** — From manifest (after 1.5) ONLY. Never hallucinate. 2–8 members, declare gaps aloud: `no testing skill found - proceeding without coverage`.

**Gate 3 — Synthesize** — Fill `templates/team-skeleton.md` per `references/synthesis-protocol.md` (topology → owner binding → contracts → assemble → sidecar). Frontmatter `name==dirname`, `description` ≤1024 chars with `Use when...`, artifact names unique, inputs only from earlier phases. Copy `scripts/forge.py` self-contained + write `.forge/manifest.json` provenance sidecar.

**Gate 4 — Validate** — `lint` enforces `team-schema.md`: name regex, description triggers, allowed frontmatter only, phase numbering `1..N`, artifact dependency order, sidecar existence, **Working directory** declared per phase + sibling-script path lint, **capabilities** manifest warn.

**Optional — Validators** — For high-stakes pipelines (payments, API routing, CI/CD): `python3 scripts/forge.py validators ./my-team --out .team/validators` generates lightweight JSON Schema files from each JSON `Outputs: ... - shape:` declaration for deterministic boundary checks.

**Enterprise — Hermetic / Security / CI** — FAANG-ready:
```bash
python3 scripts/forge.py scan --project --lock --out .team/manifest.json  # hermetic monorepo + .team/lock.json (sha256+git SHA)
python3 scripts/forge.py audit ./my-team                                  # static scan: network/privilege/secret
python3 scripts/forge.py eval ./my-team --fixtures ./tests/fixtures        # headless CI: lint+validators+trace → .team/trace.json
```

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
Working directory: `project root` or `~/path/to/skill` (use skill dir for ./scripts/*)
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
Skill-Forge/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Headless forge eval + lint testing
│       └── security-audit.yml     # forge.py audit runner
├── .forge/
│   └── manifest.json              # Sidecar manifest for skill-forge self-tracking
├── examples/
│   ├── design-review-team/        # Reference composite team
│   │   ├── SKILL.md
│   │   ├── .forge/manifest.json
│   │   └── scripts/forge.py
│   └── saas-dev-team/             # Reference fullstack squad
├── references/
│   ├── registries.json            # Curated registries for Gate 1.5 cold-start
│   ├── runtime-paths.md           # 11 project & home runtime paths
│   ├── synthesis-protocol.md      # Steps A-E: topology to contracts
│   └── team-schema.md             # Spec, frontmatter, & lint rules
├── scripts/
│   └── forge.py                   # 590-line stdlib compiler (scan/resolve/lint/eval/install)
├── templates/
│   ├── phase-contract.md          # Working dir, I/O, exit criteria template
│   └── team-skeleton.md           # Master Jinja-style team template
├── tests/
│   ├── fixtures/                  # Mock payloads for headless CI
│   └── test_compiler.py           # Unit tests for DAG loops, regex, & hashes
├── .gitignore
├── .gitattributes
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
└── SKILL.md                       # Root compiler skill (Gates 0-5 + 1.5)
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
