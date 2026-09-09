#!/usr/bin/env python3
"""Safely distribute repo-owned Agent Skills to supported local agents.

Dry-run is the default. Only directories recorded in each target's state file are
ever replaced or pruned without --adopt-existing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

STATE_FILE = ".skills-managed.json"
# Installs made before the state file was renamed. Still read so an existing
# installation keeps its ownership records instead of colliding with itself.
LEGACY_STATE_FILES = (".harness-managed.json",)
IGNORED_NAMES = {".git", "__pycache__", ".DS_Store"}


class DistributionError(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_manifest(source: Path) -> dict:
    path = source / "skill-profiles.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistributionError(f"cannot read {path}: {exc}") from exc
    if data.get("schema_version") != 1:
        raise DistributionError("unsupported skill-profiles.json schema_version")
    return data


def parse_skill_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", text)
    if not match:
        raise DistributionError(f"missing name frontmatter: {path}")
    return match.group(1).strip()


def discover_skills(source: Path) -> dict[str, Path]:
    skills: dict[str, Path] = {}
    declared_names: set[str] = set()
    for child in sorted(source.iterdir()):
        skill_file = child / "SKILL.md"
        if not child.is_dir() or not skill_file.is_file():
            continue
        name = parse_skill_name(skill_file)
        if name != child.name and not name.endswith(f":{child.name}"):
            raise DistributionError(
                f"skill name/folder mismatch: {child.name!r} != {name!r}"
            )
        if name in declared_names:
            raise DistributionError(f"duplicate skill name: {name}")
        declared_names.add(name)
        skills[child.name] = child
    return skills


def select_skills(manifest: dict, available: dict[str, Path], profile: str) -> list[str]:
    profiles = manifest.get("profiles", {})
    if profile not in profiles:
        raise DistributionError(f"unknown profile {profile!r}; choose from {sorted(profiles)}")
    configured = profiles[profile]
    selected = sorted(available) if configured == "*" else list(configured)
    missing = sorted(set(selected) - set(available))
    if missing:
        raise DistributionError(f"profile {profile!r} names missing skills: {missing}")
    retired = set(manifest.get("retired_skills", []))
    selected_retired = sorted(retired.intersection(selected))
    if selected_retired:
        raise DistributionError(f"profile {profile!r} includes retired skills: {selected_retired}")
    return selected


def file_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in IGNORED_NAMES for part in rel.parts) or path.is_dir():
            continue
        digest.update(rel.as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def ignore_copy(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES or name.endswith(".pyc")}


def state_path(target: Path) -> Path | None:
    """Return the target's ownership file, honouring the pre-rename name."""
    for name in (STATE_FILE, *LEGACY_STATE_FILES):
        candidate = target / name
        if candidate.exists():
            return candidate
    return None


def read_state(target: Path) -> dict:
    path = state_path(target)
    if path is None:
        return {"schema_version": 1, "managed_skills": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistributionError(f"cannot read state {path}: {exc}") from exc
    if state.get("schema_version") != 1:
        raise DistributionError(f"unsupported state schema in {path}")
    return state


def write_state(target: Path, source: Path, profile: str, skills: list[str]) -> None:
    payload = {
        "schema_version": 1,
        "source": str(source.resolve()),
        "profile": profile,
        "managed_skills": sorted(skills),
    }
    temporary = target / f"{STATE_FILE}.tmp"
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target / STATE_FILE)
    for name in LEGACY_STATE_FILES:
        legacy = target / name
        if legacy.exists():
            legacy.unlink()


def resolve_targets(manifest: dict, home: Path, requested: list[str] | None) -> dict[str, Path]:
    configured = manifest.get("targets", {})
    if requested:
        names = list(configured) if requested == ["all"] else requested
        unknown = sorted(set(names) - set(configured))
        if unknown:
            raise DistributionError(f"unknown targets: {unknown}")
        return {name: home / configured[name] for name in names}

    detected = {
        name: home / rel
        for name, rel in configured.items()
        if (home / Path(rel).parent).exists()
    }
    if not detected:
        raise DistributionError("no agent configuration directories detected; pass --target")
    return detected


def plan_target(
    target: Path,
    selected: list[str],
    previous: set[str],
    adopt_existing: bool,
    prune: bool,
) -> tuple[list[str], list[str]]:
    collisions = [
        name for name in selected if (target / name).exists() and name not in previous
    ]
    if collisions and not adopt_existing:
        raise DistributionError(
            f"{target}: unmanaged skill directories would be replaced: {collisions}; "
            "inspect them, then rerun with --adopt-existing"
        )
    removals = sorted(previous - set(selected)) if prune else []
    return collisions, removals


def apply_target(
    target: Path,
    available: dict[str, Path],
    selected: list[str],
    removals: list[str],
    source: Path,
    profile: str,
) -> None:
    target.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".skills-staging-", dir=target))
    backup = Path(tempfile.mkdtemp(prefix=".skills-backup-", dir=target))
    replaced: list[str] = []
    pruned: list[str] = []
    try:
        for name in selected:
            shutil.copytree(available[name], staging / name, ignore=ignore_copy)
        for name in selected:
            destination = target / name
            if destination.exists():
                os.replace(destination, backup / name)
                replaced.append(name)
            os.replace(staging / name, destination)
        for name in removals:
            destination = target / name
            if destination.exists():
                os.replace(destination, backup / f"pruned-{name}")
                pruned.append(name)
        for name in selected:
            if file_digest(available[name]) != file_digest(target / name):
                raise DistributionError(f"post-copy digest mismatch: {target / name}")
        write_state(target, source, profile, selected)
    except Exception:
        for name in selected:
            destination = target / name
            if destination.exists() and name not in replaced:
                shutil.rmtree(destination)
        for name in replaced:
            destination = target / name
            if destination.exists():
                shutil.rmtree(destination)
            if (backup / name).exists():
                os.replace(backup / name, destination)
        for name in pruned:
            destination = target / name
            if destination.exists():
                shutil.rmtree(destination)
            saved = backup / f"pruned-{name}"
            if saved.exists():
                os.replace(saved, destination)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        shutil.rmtree(backup, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repo_root())
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--profile", default="core")
    parser.add_argument(
        "--target",
        action="append",
        help="agents, codex, claude, cursor, opencode, or all; repeatable",
    )
    parser.add_argument("--apply", action="store_true", help="perform the planned writes")
    parser.add_argument(
        "--adopt-existing",
        action="store_true",
        help="allow first-run replacement of same-name unmanaged skill directories",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="remove skills previously managed by this tool but absent from the profile",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.source.resolve()
    try:
        manifest = load_manifest(source)
        available = discover_skills(source)
        selected = select_skills(manifest, available, args.profile)
        targets = resolve_targets(manifest, args.home.resolve(), args.target)
        plans = []
        for name, target in targets.items():
            state = read_state(target)
            previous = set(state.get("managed_skills", []))
            collisions, removals = plan_target(
                target, selected, previous, args.adopt_existing, args.prune
            )
            plans.append((name, target, collisions, removals))

        for name, target, collisions, removals in plans:
            print(
                f"{name}: target={target} install={len(selected)} "
                f"adopt={len(collisions)} prune={len(removals)}"
            )
        if not args.apply:
            print("DRY_RUN: no files changed; pass --apply to execute")
            return 0

        for _name, target, _collisions, removals in plans:
            apply_target(target, available, selected, removals, source, args.profile)
        print(f"SYNC_OK: {len(selected)} skills -> {len(plans)} targets")
        return 0
    except DistributionError as exc:
        print(f"SYNC_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
