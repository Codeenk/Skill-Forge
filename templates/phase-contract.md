### Phase N: kebab-case-title
Owner: `owner-skill-name`
Read first: `~/path/to/owner/SKILL.md`
Working directory: `project root` (default) or `~/path/to/skill` — use skill dir when executing sibling scripts like `./scripts/helper.sh`
Objective: One verifiable sentence.
Inputs: `.team/artifacts/from-previous-phase.json` (produced by Phase N-1) or `(none)`
Actions:
1. Apply the owner skill's method to the inputs toward the objective.
2. Produce the output artifact in the exact shape below.
3. Self-check against Exit criteria before declaring the phase done.
Outputs: `.team/artifacts/<name>.<ext>` - shape: e.g. JSON with top-level keys `routes[]`, `models[]`; or markdown with sections `headline`, `body`, `ctas[3]`
Exit: Artifact exists, parses, and contains every declared key/section.
Fallback: On missing inputs or unapplicable owner instructions: produce best-effort output, mark deviation in completion report, continue to next phase unless outputs are unproducible, then stop and explain.
