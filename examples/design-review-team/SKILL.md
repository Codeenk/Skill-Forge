---
name: design-review-team
description: Compiles installed design and research skills into a coordinated workflow that produces a high-fidelity design concept and an expert critique before any code is written. Use when the user wants a designed prototype reviewed end to end, asks to combine design exploration with expert review, or mentions hi-fi concepts, design critique, or review-before-build workflows.
metadata:
  generator: skill-forge
  generated_at: 2026-08-27T00:00:00Z
  schema: skill-forge/team@1
  roster: huashu-design
---

# Design Review Team

This bundle acts as a two-phase studio: the `huashu-design` skill first drives concept production, then its own reviewer methodology is applied as a second phase against the produced artifact, yielding both a deliverable and an actionable critique.

## How this runs

Activated whenever a request matches this team's purpose. Work executes through the phases below.

## Operating rules

- Read each phase's owner skill file at phase start. Do not load them all upfront.
- All inter-phase data passes through files under `.team/artifacts/`.
- Before starting a phase, confirm its listed input artifacts exist; if missing, re-run the producing phase rather than improvising content.
- If an owner skill path does not resolve, locate it by searching for `**/<owner-name>/SKILL.md` under `$HOME` and the project root before failing.
- After the final phase, run `python3 <this-bundle>/scripts/forge.py verify .` if shell access exists; skip silently otherwise.

## Team roster

| Skill | Path | Role in this team |
|-------|------|-------------------|
| huashu-design | `~/.agents/skills/huashu-design/SKILL.md` | Produces hi-fi concept (Phase 1) and applies its expert-review method in Phase 2 |

## Phase workflow

### Phase 1: concept-production
Owner: `huashu-design`
Read first: `~/.agents/skills/huashu-design/SKILL.md`
Objective: Produce one complete hi-fi HTML design concept matching the user's brief.
Inputs: `(none)`
Actions:
1. Follow the owner skill's Junior Designer workflow from assumption notes onward.
2. Deliver a single runnable HTML artifact per the owner's conventions.
3. Record chosen direction and key assumptions.
Outputs: `.team/artifacts/concept.html` - runnable hi-fi page; `.team/artifacts/concept-notes.md` - sections `direction`, `assumptions[]`
Exit: Both artifacts exist; concept.html is non-trivially sized; concept-notes.md contains all declared sections.
Fallback: If the owner skill cannot be located, stop immediately: without the owner this team has no capability.

### Phase 2: expert-critique
Owner: `huashu-design` (expert-review mode)
Read first: `~/.agents/skills/huashu-design/SKILL.md`
Objective: Critique the Phase 1 concept using the owner's expert-review criteria.
Inputs: `.team/artifacts/concept.html`, `.team/artifacts/concept-notes.md` (produced by Phase 1)
Actions:
1. Re-open the owner skill's expert-review reference material only.
2. Score the Phase 1 output on the owner's five dimensions with justification.
3. List concrete fixes ranked by severity.
Outputs: `.team/artifacts/critique.md` - sections `scores[5]`, `fixes[{severity, item}]`
Exit: critique.md exists and lists all five dimension scores plus at least three fixes.
Fallback: If Phase 1 artifacts are malformed rather than missing, score what exists and mark deviation in the completion report.

## Completion report

After the final phase passes its exit criteria, write `.team/report.md` containing: per-phase status (done/deviated), artifact list with one-line summaries, any deviations noted in Fallback usage.
