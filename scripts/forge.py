import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PHASE_RE = re.compile(r"^###\s+Phase\s+(\d+)\b")
ARTIFACT_RE = re.compile(r"`(\.team/artifacts/[^`\s]+)`")
READ_FIRST_RE = re.compile(r"Read first:\s*`([^`]+?)`")
WORKING_DIR_RE = re.compile(r"Working directory:\s*`([^`]+)`")
SHAPE_RE = re.compile(r"shape:\s*(.+)", re.I)

PROJECT_ROOTS = [
    ".agents/skills",
    ".claude/skills",
    ".cursor/skills",
    ".codex/skills",
    ".gemini/skills",
    ".opencode/skills",
    ".opencode/skill",
    ".windsurf/skills",
    ".factory/skills",
    ".github/skills",
    ".roo/skills",
    ".kiro/skills",
]

HOME_ROOTS = [
    "~/.agents/skills",
    "~/.claude/skills",
    "~/.cursor/skills",
    "~/.codex/skills",
    "~/.gemini/skills",
    "~/.config/opencode/skills",
    "~/.opencode/skills",
    "~/.opencode/skill",
    "~/.windsurf/skills",
    "~/.factory/skills",
    "~/.kilocode/skills",
    "~/.goose/skills",
]


def sha256_16(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()[:16]


def split_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, text
    raw = {}
    cur = None
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val:
                raw[key] = val.strip("'\"")
                cur = key if val in ("", "{}") else None
            else:
                raw[key] = {}
                cur = key
        elif cur and re.match(r"^\s+(\S)", line) and isinstance(raw.get(cur), dict):
            mm = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", line)
            if mm:
                raw[cur][mm.group(1)] = mm.group(2).strip().strip("'\"")
    body = "\n".join(lines[end + 1 :])
    return raw, body


def load_skill(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    fm, body = split_frontmatter(text)
    return fm, body


def iter_roots():
    seen = set()
    out = []
    for label, base, rel in [("project", ".", p) for p in PROJECT_ROOTS] + [
        ("home", "~", h) for h in HOME_ROOTS
    ]:
        path = os.path.abspath(os.path.join(base, rel)) if base == "." else os.path.expanduser(rel)
        if path in seen or not os.path.isdir(path):
            continue
        seen.add(path)
        out.append((label, path))
    extra = os.environ.get("FORGE_EXTRA_ROOTS", "")
    for part in extra.split(":"):
        part = part.strip()
        if part:
            path = os.path.expanduser(part)
            if path not in seen and os.path.isdir(path):
                seen.add(path)
                out.append(("env", path))
    return out


def cmd_scan(args):
    skills = []
    n_roots = 0
    for label, root in iter_roots():
        n_roots += 1
        for entry in sorted(os.listdir(root)):
            skill_md = os.path.join(root, entry, "SKILL.md")
            if not os.path.isfile(skill_md):
                continue
            real = os.path.realpath(skill_md)
            if any(s["realpath"] == real for s in skills):
                continue
            try:
                fm, body = load_skill(skill_md)
            except Exception as e:
                print(f"WARN unreadable {skill_md}: {e}", file=sys.stderr)
                continue
            with open(skill_md, "rb") as f:
                digest = sha256_16(f.read())
            d = os.path.dirname(skill_md)
            skills.append(
                {
                    "name": fm.get("name") or entry,
                    "dirname": entry,
                    "description": fm.get("description", ""),
                    "root_label": label,
                    "root": root,
                    "abs_skill_md": skill_md,
                    "realpath": real,
                    "hash": digest,
                    "body_lines": body.count("\n") + 1,
                    "has_scripts": os.path.isdir(os.path.join(d, "scripts")),
                    "has_references": os.path.isdir(os.path.join(d, "references")),
                }
            )
    manifest = {
        "schema": "skill-forge/manifest@1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "workspace": os.getcwd(),
        "roots_scanned": [p for _, p in iter_roots()],
        "skill_count": len(skills),
        "skills": skills,
    }
    out_path = args.out
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"scan: {len(skills)} skills across {n_roots} roots -> {out_path}")
    for s in skills:
        desc = s["description"][:70] + ("..." if len(s["description"]) > 70 else "")
        print(f"  [{s['root_label']:7}] {s['name']:<28} {digest[-8:] if False else s['hash'][-6:]} {desc}")
    return 0


def cmd_lint(args):
    errors, warns = [], []
    d = args.dir
    skill_md = os.path.join(d, "SKILL.md")
    if not os.path.isfile(skill_md):
        print(f"lint: FAIL {skill_md} missing")
        return 1
    fm, body = load_skill(skill_md)
    md = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    team_mode = str(md.get("schema", "")).startswith("skill-forge/team")
    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        errors.append("frontmatter missing 'name'")
    elif len(name) > 64 or not NAME_RE.match(name):
        errors.append(f"name '{name}' violates spec (lowercase alnum + single hyphens, <=64)")
    if name and os.path.basename(os.path.abspath(d)) != name:
        errors.append(f"name '{name}' != directory name '{os.path.basename(os.path.abspath(d))}'")
    if not desc:
        errors.append("frontmatter missing 'description'")
    else:
        if len(desc) > 1024:
            errors.append(f"description {len(desc)} chars > 1024 spec limit")
        if not re.search(r"use when|use this|when the user", desc, re.I):
            warns.append("description lacks trigger phrase ('Use when ...') - auto-triggering will be weak")
    forbidden = set(fm) - {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    if forbidden:
        errors.append(f"non-spec frontmatter keys: {sorted(forbidden)}")
    n_lines = body.count("\n") + 1
    if n_lines > 500:
        warns.append(f"body {n_lines} lines > 500 spec recommendation - move detail to references/")
    phase_nums = []
    outputs_at = {}
    inputs_at = {}
    artifacts_all = []
    cur = None
    for i, line in enumerate(body.splitlines()):
        pm = PHASE_RE.match(line)
        if pm:
            cur = int(pm.group(1))
            phase_nums.append(cur)
            outputs_at[cur], inputs_at[cur] = [], []
        arts = ARTIFACT_RE.findall(line)
        artifacts_all.extend(arts)
        if cur is None:
            continue
        if re.match(r"^\s*Outputs?:", line):
            outputs_at[cur].extend(a for a in arts if ".team/artifacts/" in a)
        elif re.match(r"^\s*Inputs?:", line):
            inputs_at[cur].extend(a for a in arts if ".team/artifacts/" in a)
    if not phase_nums:
        if team_mode:
            errors.append("no '### Phase N:' blocks found")
        else:
            warns.append("no '### Phase N:' blocks (not a team bundle - skipping contract checks)")
    else:
        expected = list(range(1, len(phase_nums) + 1))
        if phase_nums != expected:
            errors.append(f"phase numbering broken: {phase_nums} != {expected}")
        producers = {}
        for ph, outs in outputs_at.items():
            for a in outs:
                if a in producers:
                    errors.append(f"artifact {a} declared as Output by both Phase {producers[a]} and Phase {ph}")
                producers[a] = ph
        if len(producers) < 2:
            warns.append("<2 distinct artifacts - this looks like a wrapper, not a multi-phase team")
        for ph, ins in inputs_at.items():
            for a in ins:
                src = producers.get(a)
                if src is None:
                    warns.append(f"Phase {ph} input {a} has no producing phase")
                elif src >= ph:
                    errors.append(f"Phase {ph} consumes {a} produced by Phase {src} (forward/circular dependency)")
    owner_paths = READ_FIRST_RE.findall(body)
    working_dirs = WORKING_DIR_RE.findall(body)
    if team_mode:
        for p in owner_paths:
            resolved = os.path.expanduser(p)
            if "$HOME" in p or "<this-bundle>" in p:
                continue
            if not os.path.isabs(resolved) and not resolved.startswith("/"):
                resolved = os.path.join(d, resolved)
            if not os.path.exists(resolved):
                warns.append(f"owner path does not exist on this machine: {p}")
        if len(owner_paths) < max(len(phase_nums) - 1, 1):
            warns.append("some phases lack an explicit 'Read first:' owner pointer")
        if len(working_dirs) < len(phase_nums):
            warns.append(f"only {len(working_dirs)}/{len(phase_nums)} phases declare Working directory — add explicit Working directory per phase-contract.md to avoid cwd ambiguity")
        if "./scripts/" in body or "../references/" in body:
            for ph in phase_nums:
                block = body.split(f"### Phase {ph}:")[1].split("### Phase ")[0] if f"### Phase {ph}:" in body else ""
                has_relative = "./scripts/" in block or "../references/" in block
                has_skill_cwd = "skill" in block.lower() and "working directory" in block.lower()
                if has_relative and not has_skill_cwd:
                    warns.append(f"Phase {ph} references sibling scripts (./scripts/ or ../references/) but Working directory is not set to skill source dir — use absolute/home-relative paths")
        sidecar = os.path.join(d, ".forge", "manifest.json")
        if not os.path.isfile(sidecar):
            errors.append(".forge/manifest.json sidecar missing on generator-produced bundle")
        else:
            with open(sidecar, encoding="utf-8") as f:
                sc = json.load(f)
            if not isinstance(sc.get("roster"), list) or not sc["roster"]:
                errors.append("sidecar roster empty/malformed")
        unref = [a for a in set(artifacts_all) if a not in producers]
        if unref:
            warns.append(f"artifact mentions without production declaration: {sorted(unref)}")
    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    if errors:
        print(f"lint: FAIL ({len(errors)} errors, {len(warns)} warnings)")
        return 1
    print(f"lint: PASS ({len(warns)} warnings)")
    return 0


def cmd_validators(args):
    d = args.dir
    out = os.path.expanduser(args.out)
    skill_md = os.path.join(d, "SKILL.md")
    if not os.path.isfile(skill_md):
        print(f"validators: FAIL {skill_md} missing")
        return 1
    _, body = load_skill(skill_md)
    os.makedirs(out, exist_ok=True)
    generated = 0
    for line in body.splitlines():
        if "Outputs:" not in line or ".team/artifacts/" not in line:
            continue
        m_art = ARTIFACT_RE.search(line)
        if not m_art:
            continue
        art = m_art.group(1)
        if not art.endswith(".json"):
            continue
        m_shape = SHAPE_RE.search(line)
        shape = m_shape.group(1) if m_shape else ""
        keys = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\[|\{|,)", shape)
        keys = [k for k in keys if k not in {"JSON","json","keys","key","with","and","or","shape","top","level","sections"}]
        seen = []
        for k in keys:
            if k not in seen:
                seen.append(k)
        keys = seen
        if not keys:
            keys = ["_placeholder"]
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": os.path.basename(art),
            "type": "object",
            "required": keys if keys != ["_placeholder"] else [],
            "properties": {k: {} for k in keys if k != "_placeholder"},
            "additionalProperties": True,
        }
        base = os.path.splitext(os.path.basename(art))[0]
        out_path = os.path.join(out, f"{base}.schema.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        print(f"validator {base}.schema.json  required: {keys}")
        generated += 1
    if generated == 0:
        print(f"validators: no JSON Outputs found in {skill_md} — nothing generated")
        return 0
    print(f"validators: {generated} schema(s) -> {out}")
    return 0


def runtime_targets(extra_into=None):
    roots = iter_roots()
    if extra_into:
        p = os.path.expanduser(extra_into)
        return [("manual", p)]
    out = []
    for label, root in roots:
        if any(root.endswith(r) and ("skills" in root or "skill" in root) for r in PROJECT_ROOTS + HOME_ROOTS) or True:
            if os.path.basename(root) in ("skills", "skill"):
                out.append((label, root))
    return out


def cmd_install(args):
    d = args.dir
    src = os.path.abspath(d)
    if not os.path.isfile(os.path.join(src, "SKILL.md")):
        print(f"install: FAIL {src}/SKILL.md missing")
        return 1
    name = args.name
    if not name:
        fm, _ = load_skill(os.path.join(src, "SKILL.md"))
        name = fm.get("name") or os.path.basename(src)
    targets = runtime_targets(args.into)
    if not targets:
        print("install: no runtime skill roots detected on this machine")
        print("options:")
        print("  npx skills add '" + src + "'")
        print("  python3 scripts/forge.py install <team-dir> --into ~/.yourclient/skills")
        return 1
    installed = 0
    for label, root in targets:
        os.makedirs(root, exist_ok=True)
        dest = os.path.join(root, name)
        if os.path.exists(dest) and not args.force:
            print(f"SKIP   {dest} (exists, use --force)")
            continue
        if os.path.exists(dest):
            shutil.rmtree(dest) if os.path.isdir(dest) else os.remove(dest)
        if args.link:
            os.symlink(src, dest)
        else:
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__"))
        print(f"INSTALL[{label:7}] {dest}")
        installed += 1
    print(f"install: {installed} runtime(s)")
    return 0 if installed or args.force else 1


def cmd_verify(args):
    d = args.dir
    sidecar = os.path.join(d, ".forge", "manifest.json")
    if not os.path.isfile(sidecar):
        print(f"verify: FAIL no sidecar at {sidecar}")
        return 2
    with open(sidecar, encoding="utf-8") as f:
        sc = json.load(f)
    bad = 0
    for member in sc.get("roster", []):
        path = member["path"]
        want = member["hash"]
        real = os.path.expanduser(path)
        if not os.path.isfile(real):
            print(f"MISSING {member['skill']:<28} {path}")
            bad += 1
            continue
        with open(real, "rb") as f2:
            have = sha256_16(f2.read())
        if have != want:
            print(f"DRIFTED {member['skill']:<28} {want[-6:]} -> {have[-6:]}  rerun synthesis")
            bad += 1
        else:
            print(f"OK      {member['skill']:<28} {have[-6:]}")
    status = "FAIL" if bad else "PASS"
    print(f"verify: {status} ({bad} drifted/missing of {len(sc.get('roster', []))})")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(prog="forge.py", description="skill-forge tooling (stdlib-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="discover all installed skills into a manifest")
    s.add_argument("--out", default=".forge/manifest.json")
    s.set_defaults(fn=cmd_scan)

    l = sub.add_parser("lint", help="validate a bundle against the team-schema contract")
    l.add_argument("dir")
    l.set_defaults(fn=cmd_lint)

    i = sub.add_parser("install", help="mirror a validated bundle into every detected runtime root")
    i.add_argument("dir")
    i.add_argument("--into", default=None, help="explicit target skills dir (overrides detection)")
    i.add_argument("--link", action="store_true", help="symlink instead of copying")
    i.add_argument("--force", action="store_true", help="overwrite existing install")
    i.add_argument("--name", default=None, help="override install dir name")
    i.set_defaults(fn=cmd_install)

    v = sub.add_parser("verify", help="check roster drift via the bundle's sidecar")
    v.add_argument("dir")
    v.set_defaults(fn=cmd_verify)

    gv = sub.add_parser("validators", help="generate lightweight JSON Schema validators from Outputs shapes")
    gv.add_argument("dir", help="team bundle dir containing SKILL.md")
    gv.add_argument("--out", default=".team/validators", help="output dir for *.schema.json (default: .team/validators)")
    gv.set_defaults(fn=cmd_validators)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
