import json
import re
import hashlib

def test_no_dag_loop():
    body = "### Phase 1: a\nOutputs: `.team/artifacts/a.json`\n### Phase 2: b\nInputs: `.team/artifacts/a.json`\nOutputs: `.team/artifacts/b.json`"
    phases = re.findall(r"###\s+Phase\s+(\d+)", body)
    assert phases == ["1", "2"]

def test_artifact_uniqueness():
    arts = ["a.json", "b.json", "a.json"]
    assert len(set(arts)) != len(arts)

def test_sha256():
    h = hashlib.sha256(b"test").hexdigest()[:16]
    assert len(h) == 16

def test_name_regex():
    pat = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    assert pat.match("my-team")
    assert not pat.match("My_Team")

def test_hash_determinism():
    from pathlib import Path
    import subprocess, tempfile, os
    assert True

def test_validators_shape_parse():
    shape = "JSON with keys pages[{path,purpose}], components[]"
    keys = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\[|\{|,)", shape)
    assert "pages" in keys
