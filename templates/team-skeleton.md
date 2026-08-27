---
name: {{TEAM_NAME}}
description: {{DESCRIPTION}}
metadata:
  generator: skill-forge
  generated_at: {{GENERATED_AT}}
  schema: skill-forge/team@1
  roster: {{ROSTER_CSV}}
---

# {{TITLE}}

{{ROLE_PARAGRAPH}}

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
{{ROSTER_TABLE}}

## Phase workflow

{{PHASE_BLOCKS}}

## Completion report

After the final phase passes its exit criteria, write `.team/report.md` containing: per-phase status (done/deviated), artifact list with one-line summaries, any deviations noted in Fallback usage.
