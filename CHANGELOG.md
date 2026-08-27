# Changelog

All notable changes to Skill-Forge are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/).

## [1.2.0] - 2026-08-27
### Added
- Gate 1.5 cold-start: curated `registries.json` + `resolve --need` → `.forge/vendor` (hermetic) / `--global`
- `scan --project --lock` hermetic monorepo + `.team/lock.json` (sha256+git SHA)
- `audit` static AST scan (network/privilege/secret) + `capabilities` manifest
- `eval` headless CI + `.team/trace.json` (OTel)
- `validators` JSON Schema from `Outputs: shape:`
- `Working directory:` per phase contract

## [1.1.0] - 2026-08-27
### Added
- Explicit `Working directory` in phase contracts
- Optional `validators` generation

## [1.0.0] - 2026-08-27
### Added
- Initial compiler: `scan`, `lint`, `install`, `verify` — 5-gate pipeline
