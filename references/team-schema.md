# Output Contract: Generated Team Bundle

Every forge-produced bundle must satisfy this contract. It is the checklist used by `scripts/forge.py lint`.

## Directory layout

```
<team-name>/                  REQUIRED: dirname == frontmatter name
├── SKILL.md                  required, <500 lines
├── .forge/
│   └── manifest.json         provenance sidecar
└── scripts/
    └── forge.py              copied verbatim from the forge bundle
```

Reference docs referenced *by* the team body live in `<team-name>/references/*.md` when needed (keep one level deep).

## Frontmatter rules

| Field | Rule |
|---|---|
| `name` | 1-64 chars, `[a-z0-9]` + single hyphens, must equal directory name |
| `description` | 1-1024 chars. MUST contain: what the team does + trigger phrase "Use when the user wants ..." + 3+ concrete task keywords |
| `metadata` | string→string map. Recommended keys: `generator`, `generated_at`, `schema`, `roster` (comma-joined skill names) |
| `license` | optional, copy choice from source skills if uniform, else omit |
| `compatibility` | include ONLY if a roster member truly requires it |

Prohibited: any key outside the spec table (no `mode:`, no `model:`, no `tools:`).

## Sidecar schema (.forge/manifest.json)

```json
{
  "schema": "skill-forge/sidecar@1",
  "generator": "skill-forge",
  "generated_at": "<ISO-8601>",
  "source_workspace": "<cwd at synthesis>",
  "roster": [
    {"skill": "express-backend", "path": "~/.agents/skills/express-backend/SKILL.md", "hash": "sha256:<16hex-prefix>"}
  ],
  "entry_points": ["<team-dir>/SKILL.md"]
}
```

The sidecar is DATA for tools (`verify` consumes it). The SKILL.md body must stay human-readable without consulting it.

## Body structure (in order)

1. `# Title` + 1-paragraph role definition ("This bundle acts as ...").
2. `## How this runs` - two sentences max: triggered by description match; work executes in phases below.
3. `## Operating rules` - always exactly these five bullets (boilerplate kept identical across all generated teams):
   - Read each phase's owner skill file at phase start. Do not load them all upfront.
   - All inter-phase data passes through files under `.team/artifacts/`.
   - Before starting a phase, confirm its listed input artifacts exist; if missing, re-run the producing phase, do not improvise content.
   - If an owner skill path does not resolve, locate it by searching for `**/<owner-name>/SKILL.md` under `$HOME` and the project root before failing.
   - After the final phase, run `python3 <team-dir>/scripts/forge.py verify <team-dir>` if shell access exists, else skip silently.
4. `## Phase workflow` - ordered `### Phase N:` blocks (schema below).
5. `## Completion report` - instructs writing `.team/report.md`: per-phase status, artifact list, deviations.

## Phase block schema

```markdown
### Phase N: <kebab-case-title>
Owner: `skill-name`
Read first: `~/path/to/owner/SKILL.md`
Objective: <one sentence>
Inputs: <artifact paths or "(none)">
Actions: <numbered instructions referencing the OWNER skill's method, not replacing it>
Outputs: `.team/artifacts/<name>.<ext>` - <shape: json keys | md sections | etc>
Exit: <objectively checkable condition>
Fallback: <what to do if owner skill cannot be followed>
```

Rules enforced by lint:
- Phase numbers start at 1 and increase by 1.
- Every block defines Owner, Outputs, Exit.
- An input artifact for phase N may only be produced by phase M where M < N.
- All `artifacts/...` names unique across Outputs lines.
- First phase typically has `(none)` inputs; last phase must define a consumer-visible final artifact or report.
