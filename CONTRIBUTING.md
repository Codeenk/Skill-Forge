# Contributing to Skill-Forge

Thank you for contributing! Skill-Forge is stdlib-only Python, so contributions stay lean.

## Quick Start
```bash
git clone https://github.com/Codeenk/Skill-Forge.git
cd Skill-Forge
python3 scripts/forge.py scan --out .team/manifest.json
python3 scripts/forge.py lint ./
python3 -m pytest tests/ -v
```

## Pull Requests
1. Fork, create branch `feat/your-feature`.
2. Run `python3 scripts/forge.py lint ./` and `python3 scripts/forge.py audit ./` — must PASS.
3. Add tests in `tests/test_compiler.py` if you change `forge.py`.
4. Open PR — CI runs headless eval + validators.

## Adding a Skill to Registries
Edit `references/registries.json` allowlist; PR must include `audit PASS` log.

## Code Style
- Python 3.9+, no external deps.
- Keep `SKILL.md` <500 lines, use `Read first:` progressive disclosure.

## License
By contributing you agree your contributions are MIT licensed.
