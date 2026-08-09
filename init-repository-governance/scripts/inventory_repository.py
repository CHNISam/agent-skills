#!/usr/bin/env python3
"""Print a read-only repository inventory for AGENTS.md authoring."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


INTERESTING_FILES = (
    "AGENTS.md",
    "AGENTS.override.md",
    "CLAUDE.md",
    "README.md",
    "CONTRIBUTING.md",
    "package.json",
    "pnpm-workspace.yaml",
    "yarn.lock",
    "package-lock.json",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "Makefile",
    "Taskfile.yml",
    "docker-compose.yml",
    "compose.yml",
)

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next", ".venv", "venv"}


def git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def discover(root: Path) -> list[str]:
    found: list[str] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() and (path.name in INTERESTING_FILES or path.parent.name in {".github", ".gitlab"}):
            found.append(path.relative_to(root).as_posix())
    return sorted(found)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    payload = {
        "root": str(root),
        "git_toplevel": git(root, "rev-parse", "--show-toplevel"),
        "git_branch": git(root, "branch", "--show-current"),
        "git_status": git(root, "status", "--short", "--branch"),
        "git_remotes": git(root, "remote", "-v"),
        "candidate_files": discover(root),
        "top_level_directories": sorted(p.name for p in root.iterdir() if p.is_dir() and p.name not in SKIP_DIRS),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
