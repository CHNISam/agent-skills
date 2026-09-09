#!/usr/bin/env python3
"""Validate this repository's own structural and routing invariants."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    fields: dict[str, str] = {}
    current = None
    for line in text[4:end].splitlines():
        if ":" in line and not line[:1].isspace():
            key, value = line.split(":", 1)
            current = key.strip()
            fields[current] = value.strip().strip("'\"")
        elif current and line[:1].isspace() and not fields[current]:
            fields[current] = line.strip()
    return fields


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "skill-profiles.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot read skill-profiles.json: {exc}"]

    skills: dict[str, Path] = {}
    for child in sorted(root.iterdir()):
        skill_file = child / "SKILL.md"
        if not child.is_dir() or not skill_file.is_file():
            continue
        fields = frontmatter(skill_file.read_text(encoding="utf-8"))
        name = fields.get("name")
        description = fields.get("description")
        if not name:
            errors.append(f"{skill_file}: missing simple name frontmatter")
            continue
        if name != child.name and not name.endswith(f":{child.name}"):
            errors.append(f"{skill_file}: name {name!r} does not match folder {child.name!r}")
        if name in skills:
            errors.append(f"duplicate skill name {name!r}: {skills[name]} and {skill_file}")
        skills[name] = skill_file
        if not description:
            errors.append(f"{skill_file}: missing single-line description frontmatter")

    retired = set(manifest.get("retired_skills", []))
    present_retired = sorted(retired.intersection(skills))
    if present_retired:
        errors.append(f"retired skills still discoverable at repository root: {present_retired}")

    profiles = manifest.get("profiles", {})
    if not isinstance(profiles, dict) or "core" not in profiles:
        errors.append("skill-profiles.json: profiles.core is required")
    for profile, names in profiles.items():
        if names == "*":
            continue
        if not isinstance(names, list) or len(names) != len(set(names)):
            errors.append(f"profile {profile!r} must be a duplicate-free list or '*'")
            continue
        missing = sorted(set(names) - set(skills))
        if missing:
            errors.append(f"profile {profile!r} references missing skills: {missing}")
        bad = sorted(set(names).intersection(retired))
        if bad:
            errors.append(f"profile {profile!r} references retired skills: {bad}")

    required_files = [
        "README.md",
        "NOTICE",
        "skill-profiles.json",
        "scripts/distribute_skills.py",
        "scripts/validate_repo.py",
        ".github/workflows/ci.yml",
    ]
    for rel in required_files:
        if not (root / rel).is_file():
            errors.append(f"missing required repository file: {rel}")

    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    for name in sorted(retired):
        if re.search(rf"`{re.escape(name)}`.*\b(core|on-demand)\b", readme, re.I):
            errors.append(f"README.md routes retired skill {name!r} as active")

    core = profiles.get("core")
    if isinstance(core, list):
        missing_docs = sorted(name for name in core if f"`{name}`" not in readme)
        if missing_docs:
            errors.append(f"README.md does not document core skills: {missing_docs}")
    return errors


def main() -> int:
    errors = validate(root_from_script())
    if errors:
        for error in errors:
            print(f"REPO_ERROR: {error}", file=sys.stderr)
        return 1
    print("REPO_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
