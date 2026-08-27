# Synthesis Protocol (LLM procedure for Gates 2-4)

Inputs available at this point: `.team/manifest.json` from scan, user answers from Gate 0, and the two templates ([../templates/team-skeleton.md](../templates/team-skeleton.md), [../templates/phase-contract.md](../templates/phase-contract.md)).

## Step A - Derive the topology from the INTENT, not from availability

Write down, before touching the roster: what intermediate artifacts must exist between "user prompt" and "final deliverable"? That list IS your phase spine. Availability shapes who owns phases, not how many exist. If a required discipline has no owning skill, either declare the gap or propose merging adjacent phases - do not invent a fake owner.

Decide the topology type once:
- `pipeline` - strictly linear, each phase consumes previous outputs. Default.
- `hub` - one decisive middle phase whose artifact feeds several independent downstream phases (e.g. a spec feeding frontend AND backend work).
- Do not synthesize loops. If feedback is genuinely needed, model it as an explicit re-entry instruction in the last phase's Fallback line.

## Step B - Bind owners

For each phase choose the manifest member whose description overlaps most strongly with the phase objective. Conflict rule: if two members fit, pick the narrower one (more specific description wins); put the broader one as an auxiliary read in Actions. If NO member fits a phase, stop and present the gap - never fabricate.

Cap: >8 members means you clustered wrong; regroup into fewer coarser phases.

## Step C - Draft contracts (the part that decides whether the team works)

For each phase fill the template block. Quality bar for contracts:

- Objective is verifiable: a reviewer could say yes/no it was met. Ban words like "good", "proper", "appropriate".
- Outputs specify SHAPE, e.g. `api-spec.json` with top-level keys `routes[], models[]`, or `copy.md` with sections `headline, body, ctas[3]`. Vague outputs are the #1 failure cause of composite skills.
- Exit criterion must be mechanically checkable by reading the artifact: file exists + parses + contains required keys/sections.
- Fallback states behavior when the owner skill cannot be applied (missing stack info, contradicting instructions): default is "produce best-effort artifact, mark deviation in completion report".
- Keep Actions to <=5 numbered steps; the owner skill supplies its own depth. You are choreographing, not rewriting.

## Step D - Assemble

1. Copy skeleton, replace slots.
2. Build the roster table: columns Skill / Path / Role-in-team (one-liner) / Loaded-during.
3. Insert phase blocks.
4. Write the frontmatter description LAST (you now know the real scope): pattern = "<Team> compiles N installed skills (<names>) into a coordinated workflow for <purpose>. Use when the user wants <phrasings users actually type>, asks to <verbs>, or mentions <keywords>." Verify <=1024 chars.
5. Create `.forge/manifest.json` with roster paths + hashes copied exactly from the scan manifest.
6. `cp` this bundle's `scripts/forge.py` into `<new-bundle>/scripts/forge.py`.

## Step E - Self-review before lint

Read your generated SKILL.md start-to-finish as an enemy reviewer and check:
- Could I execute Phase 1 with zero prior context? 
- Is any phase secretly relying on conversation memory?
- Does any sentence assume Claude Code specifically?
- Are artifact paths consistent everywhere they appear (typos here break handoffs)?
Then run lint and fix everything it flags, iteratively.

## Anti-patterns observed in bad team skills

- "Coordinate the frontend skill appropriately" -> tells nothing. Replace with concrete actions + artifact.
- Inlining whole sub-skills "for convenience" -> context bloat defeats progressive disclosure.
- 12 micro-phases -> coordinator overhead exceeds value; merge related steps.
- Forgetting the completion report -> teams end silently mid-chain, indistinguishable from crashes.
