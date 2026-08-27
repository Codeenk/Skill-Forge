## Pull Request

**What does this PR do?**
<!-- Describe the change, link issue -->

**How to test?**
```bash
python3 scripts/forge.py lint ./your-team
python3 scripts/forge.py audit ./your-team
```

**Checklist**
- [ ] `lint PASS`
- [ ] `audit PASS` (no network/privilege leaks)
- [ ] Updated `README` if user-facing
- [ ] Added tests for `forge.py` changes
