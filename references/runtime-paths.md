# Runtime Compatibility Matrix

The Agent Skills spec (agentskills.io) is implemented by 40+ clients: Claude Code, OpenCode, Cursor, Codex, Gemini CLI, Command Code, Goose, Amp, Roo Code, Kiro, TRAE, Copilot/VS Code, Factory Droid, Windsurf, Junie, OpenHands, Letta, pi, VT Code, fast-agent, Hermes, OpenClaw, nanobot and more.

## Why generated bundles are portable by construction

Every generated bundle uses ONLY capabilities that exist in ALL of these clients:

| Capability | Spec basis | Why it is universal |
|---|---|---|
| Frontmatter `name` + `description` | required by spec | drives auto-triggering everywhere |
| Reading a file at phase start | plain instruction | every client has file-read tools |
| Writing artifacts under `.team/artifacts/` | plain instruction | every client has file-write tools |
| Running optional python scripts | `scripts/` convention | degrade gracefully if absent (body says "skip silently") |
| `.forge/` sidecar | "any additional files or directories" | loader-ignored provenance data |

What generated bundles deliberately AVOID:
- `allowed-tools` (experimental, inconsistent support)
- proprietary frontmatter keys (`mode`, `model`, `tools`, `handoffs`)
- client-specific tool names / slash-command syntax
- absolute-only roster paths (home-relative `~/...` + glob fallback instead)

## Skill roots scanned (detection-first)

A root only counts when it ALREADY EXISTS on the machine. Order: project-relative first, then home-relative.

Project: `.agents/skills`, `.claude/skills`, `.cursor/skills`, `.codex/skills`, `.gemini/skills`, `.opencode/skills`, `.opencode/skill`, `.windsurf/skills`, `.factory/skills`, `.github/skills`, `.roo/skills`, `.kiro/skills`

Home: `~/.agents/skills`, `~/.claude/skills`, `~/.cursor/skills`, `~/.codex/skills`, `~/.gemini/skills`, `~/.config/opencode/skills`, `~/.opencode/skills`, `~/.opencode/skill`, `~/.windsurf/skills`, `~/.factory/skills`, `~/.kilocode/skills`, `~/.goose/skills`

Extend without editing code: set `FORGE_EXTRA_ROOTS="/some/root:/other/root"` (colon-separated).

Unknown client? Its skills dir still gets picked up if it matches a pattern above; otherwise install with `npx skills add <bundle>` (the ecosystem installer knows all clients) or target it manually:

```bash
python3 scripts/forge.py install <team-dir> --into ~/.yourclient/skills
```

## Invocation portability note

Clients differ ONLY in how they decide to activate a skill - matching happens on `name` + `description` per the spec's progressive disclosure model in every known implementation. Therefore the generated description field is written as trigger-rich second-person text covering the real phrasings users type. Nothing else about activation varies in ways we must handle.

## Headless smoke testing (optional CI)

Where CLIs support headless runs, teams can be exercised non-interactively:
- Claude Code: `claude -p "<golden prompt>"`
- OpenCode: `opencode run "<golden prompt>"`
- Codex: `codex exec "<golden prompt>"`

Golden prompt recipe: ask for the smallest deliverable the team produces; assert `.team/artifacts/*` files exist afterward. Keep one golden task per bundled team under version control.
