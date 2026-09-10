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
        "discovery_graph_notes.md",
        "scripts/distribute_skills.py",
        "scripts/validate_repo.py",
        "scripts/audit_catalog.py",
        ".github/workflows/ci.yml",
    ]
    for rel in required_files:
        if not (root / rel).is_file():
            errors.append(f"missing required repository file: {rel}")

    targets = manifest.get("targets", {})
    if not isinstance(targets, dict) or not targets:
        errors.append("skill-profiles.json: targets must be a non-empty object")
    discovery_graph = manifest.get("discovery_graph", {})
    if not isinstance(discovery_graph, dict) or not discovery_graph:
        errors.append("skill-profiles.json: discovery_graph is required")
    else:
        referenced_write_roots: set[str] = set()
        for agent, entry in discovery_graph.items():
            if agent == "_comment":
                continue
            roots = entry.get("roots") if isinstance(entry, dict) else None
            if not isinstance(roots, list) or not roots:
                errors.append(f"discovery_graph[{agent!r}]: roots must be a non-empty list")
                continue
            for root_entry in roots:
                write_root = root_entry.get("write_root") if isinstance(root_entry, dict) else None
                if write_root is None:
                    continue
                referenced_write_roots.add(write_root)
                if write_root not in targets:
                    errors.append(
                        f"discovery_graph[{agent!r}] names write_root {write_root!r}, "
                        f"which is not a key in targets: {sorted(targets)}"
                    )
        orphan_targets = sorted(set(targets) - referenced_write_roots)
        if orphan_targets:
            errors.append(
                f"targets has entries no discovery_graph root ever writes through: {orphan_targets}"
            )

    exceptions = manifest.get("duplicate_exceptions", [])
    if not isinstance(exceptions, list):
        errors.append("skill-profiles.json: duplicate_exceptions must be a list")
    else:
        # A waiver for the one-skill-one-entry invariant is only trustworthy if it is
        # specific: which agent, which identity, which exact paths, and why. A vague
        # entry would silently widen into a blanket exemption, which is the failure
        # mode this whole harness exists to prevent.
        agents = {a for a in discovery_graph if a != "_comment"} if isinstance(discovery_graph, dict) else set()
        for index, exception in enumerate(exceptions):
            label = f"duplicate_exceptions[{index}]"
            if not isinstance(exception, dict):
                errors.append(f"{label}: must be an object")
                continue
            for field in ("agent", "logical_id", "reason", "reviewed"):
                if not isinstance(exception.get(field), str) or not exception[field].strip():
                    errors.append(f"{label}: {field!r} must be a non-empty string")
            paths = exception.get("paths")
            if not isinstance(paths, list) or len(paths) < 2:
                errors.append(f"{label}: 'paths' must list the 2+ contributing paths")
            elif len(set(paths)) != len(paths):
                errors.append(f"{label}: 'paths' contains duplicates")
            if agents and exception.get("agent") not in agents:
                errors.append(
                    f"{label}: agent {exception.get('agent')!r} is not a discovery_graph agent "
                    f"({sorted(agents)})"
                )

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
