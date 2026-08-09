#!/usr/bin/env python3
"""Validate a generated AGENTS.md for common governance-template mistakes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PLACEHOLDER = re.compile(
    r"<(?:one-sentence repository purpose|packages/services/apps and ownership boundaries|"
    r"adjacent systems or responsibilities that belong elsewhere|verified command(?: and selection syntax)?|"
    r"verified command or [^>]+|documented branch strategy|commit convention|production branch|"
    r"release/staging/approval documentation|critical architecture or ownership invariant|"
    r"data/security invariant|compatibility or API invariant|path|scope and reason)>|\bTODO\b|\bTBD\b",
    re.IGNORECASE,
)
PROJECT_SPECIFIC_LEAKS = ("LiteTavern", "PRODUCTION_RELEASE_ENABLED")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="path to AGENTS.md")
    parser.add_argument("--max-bytes", type=int, default=16_384)
    args = parser.parse_args()
    path = Path(args.path)
    if not path.is_file():
        parser.error(f"not a file: {path}")

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []
    if path.name not in {"AGENTS.md", "AGENTS.override.md"}:
        warnings.append(f"non-standard instruction filename: {path.name}")
    if PLACEHOLDER.search(text):
        errors.append("unresolved template placeholder (angle brackets, TODO, or TBD)")
    if not re.search(r"^#\s+", text, re.MULTILINE):
        errors.append("missing top-level heading")
    size = len(text.encode("utf-8"))
    if size > args.max_bytes:
        warnings.append(f"file is {size} bytes; consider nested guidance or linked docs")
    for value in PROJECT_SPECIFIC_LEAKS:
        if value in text:
            warnings.append(f"verify source-project-specific term: {value}")
    if not re.search(r"test|check|verify|验证|测试", text, re.IGNORECASE):
        warnings.append("no visible verification guidance")
    if not re.search(r"uncommitted|working tree|未提交|工作区", text, re.IGNORECASE):
        warnings.append("no visible rule protecting existing working-tree changes")
    if not re.search(r"worktree", text, re.IGNORECASE):
        warnings.append("no visible rule isolating concurrent writers in separate Git worktrees")

    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    if errors:
        return 1
    print(f"OK: {path} ({size} bytes, {len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
