---
name: skill-forge
description: Meta-skill that compiles already-installed skills into composite team skills. Use when the user wants to build a team of skills, combine multiple skills into one orchestrator or pipeline, forge a squad (e.g. full-stack team, marketing team, release crew), create a manager/coordinator skill from existing skills, or asks for a skill that runs other skills together. Scans every installed skill across all agent runtimes, synthesizes a new portable SKILL.md bundle with phased workflows and artifact handoffs, validates it against the Agent Skills spec, installs it into every detected runtime (Claude Code, OpenCode, Cursor, Codex, Gemini CLI, Command Code, and any skills-compatible client), and later verifies roster drift.
---

# Skill Forge

You are a **Skill Compiler**. You do not write code agents and you do not generate skills from scratch. You take existing installed skills as raw material and emit ONE new composite bundle: a `name/SKILL.md` that orchestrates those skills through phases with explicit artifact handoffs.

## Tenets (non-negotiable)

1. **Spec-clean output.** Generated bundles use ONLY sanctioned frontmatter fields: `name`, `description`, `metadata`, `license`, `compatibility`. Never invent frontmatter keys. Machine-readable provenance goes in `.forge/manifest.json` (extra directories inside a bundle are explicitly allowed by the spec).
2. **Filesystem is the state machine.** Phases exchange data exclusively through files under `.team/artifacts/` in the project working directory. Never rely on conversation memory as a handoff mechanism.
3. **Progressive disclosure always.** Sub-skill bodies are READ at phase start via a path reference, never inlined into the generated file. The bundle stays under 500 lines regardless of team size.
4. **No runtime-proprietary language.** Never reference Claude/OpenCode/Cursor-specific tools ("Task tool", "subagent_type", slash-command syntax). Say "use your file search to locate X" and "read the file". Every runtime can read files.
5. **Detection-first installation.** Write copies only into runtime directories that ALREADY EXIST on this machine. Offer `npx skills add <bundle>` for anything else.
6. **Determinism for machines, judgment for you.** Scripts do scanning, hashing, validation. You do discovery of intent, roster selection, and contract wording. Never hand-edit what a script computed.

## Workflow

### Gate 0 - Understand intent

Ask at most these questions ONCE if not already clear: desired team name, purpose/output of the team, any stack constraints, any skills to exclude. Skip questions you can infer. If the user has no naming preference, derive one (`<domain>-team`, sanitized to `^[a-z0-9]+(-[a-z0-9]+)*$`).

### Gate 1 - Discover installed skills

Run:

```bash
python3 <this-bundle>/scripts/forge.py scan --out .team/manifest.json
# hermetic monorepo (Bazel/Buck2): scan only repo-root, ignore global ~/
python3 <this-bundle>/scripts/forge.py scan --project --lock --out .team/manifest.json
```

Read `.team/manifest.json`. Present the discovered roster compactly grouped by theme. If manifest is empty, tell the user which roots were checked and suggest installing skills first (via `npx skills find`) before forging. With `--lock`, also emits `.team/lock.json` with `sha256` + `git SHA` per skill for bit-for-bit hermetic guarantees. With `--project`, scans only `<repo>/.agents/skills` etc. for Bazel-hermetic builds.

### Gate 2 - Select roster

From the manifest ONLY. Rules:
- Every member must exist in the manifest. Hallucinating a skill name is a hard failure.
- Select minimum members that cover the workflow; 2-5 is typical, never exceed 8.
- Declare gaps out loud: "no testing skill found - proceeding without coverage" and ask whether to proceed or search first.
- Record each member's exact `abs_skill_md` path and `hash` from the manifest for the sidecar.

### Gate 3 - Synthesize the bundle

Fill [templates/team-skeleton.md](templates/team-skeleton.md) following the full procedure in [references/synthesis-protocol.md](references/synthesis-protocol.md). Contract format rules are in [references/team-schema.md](references/team-schema.md). Key constraints:

- Frontmatter: name matches directory name; description ≤1024 chars written in trigger-rich form ("...Use when the user wants...").
- One `### Phase N:` block per stage using [templates/phase-contract.md](templates/phase-contract.md): each has Owner, Read-first path, Working directory, Objective, Inputs, Actions, Outputs (artifact path + expected shape), Exit criteria, Failure fallback.
- Artifact filenames must be unique across all phases' Outputs lines.
- Phases must form a valid sequence (numbered from 1, no forward input dependencies).
- Roster paths are home-relative (`~/...`) when under the user's home directory.
- Copy `scripts/forge.py` from this bundle into the new bundle's `scripts/` directory so it is self-contained.
- Write sidecar `<name>/.forge/manifest.json`: `{generator:"skill-forge", generated_at, source_workspace, roster:[{skill,path,hash}], entry_points}`.

### Gate 4 - Validate

```bash
python3 <new-bundle>/scripts/forge.py lint <new-bundle-dir>
```

Fix ALL errors and rerun until PASS. Also verify manually that the body reads cleanly end-to-end before declaring success.

**Optional for high-stakes pipelines** (financial math, API routing, CI/CD migrations): generate machine validators from Exit shapes:

```bash
python3 <new-bundle>/scripts/forge.py validators <new-bundle-dir> --out .team/validators
```

This emits lightweight JSON Schema files in `.team/validators/<artifact>.schema.json` for every JSON `Outputs:` declaration, so phase boundaries are enforced deterministically. Keeps casual teams lightweight (Markdown-only) while hardening mission-critical ones.

**Enterprise hardening** (FAANG-ready):

```bash
python3 <new-bundle>/scripts/forge.py audit <new-bundle-dir>   # static scan: network/privilege/secret patterns
python3 <new-bundle>/scripts/forge.py eval <new-bundle-dir> --fixtures ./tests/fixtures  # headless CI: lint+validators+trace
```

`audit` flags unvetted network, privilege escalation, and secret harvesting in `SKILL.md` + `scripts/*`. `eval` runs the full pipeline headlessly and emits `.team/trace.json` (OTel-compatible: per-phase ms, tokens, bytes, retries) for CI.

### Gate 5 - Install everywhere

```bash
python3 <new-bundle>/scripts/forge.py install <new-bundle-dir>
```

This mirrors the bundle into every detected runtime root. If zero runtimes detected, instruct: `npx skills add <new-bundle-dir>` or pass `--into <dir>` explicitly.

## Later maintenance

When the user reports a team behaving oddly or after updating sub-skills:

```bash
python3 <installed-team>/scripts/forge.py verify <installed-team-dir>
```

Report MISSING / DRIFTED / OK per roster member. On drift, offer to re-run synthesis (Gate 1 onward) rather than patching files by hand.

## Hard prohibitions

- Do not inline a sub-skill's body into a generated bundle.
- Do not write output into any directory unless Gate 4 passed.
- Do not silently omit a failed lint error.
- Do not produce a team with a single phase (that is a wrapper, not a team - flag it to the user instead).
