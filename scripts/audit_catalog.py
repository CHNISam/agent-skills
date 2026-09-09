#!/usr/bin/env python3
"""Compute each agent's actual effective skill catalog from the live discovery graph.

`skill-profiles.json`'s `discovery_graph` records the directories each supported agent
really scans for skills (verified against each agent's own docs/source — see
`discovery_graph_notes.md`), not just the two roots this repository writes to. This
script walks those real directories on the current machine, finds every `SKILL.md`,
and reports what each agent would actually see: total unique skills, any name found at
more than one path, and which of those are the *expected* Claude+Agents overlap this
repo's design can't remove (both writable roots, identical content) versus a *problem*
(a name reachable from a root this repo does not manage, or two different contents
under one name) that indicates leftover/stale placement.

Read-only. Never writes anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_manifest(source: Path) -> dict:
    path = source / "skill-profiles.json"
    return json.loads(path.read_text(encoding="utf-8"))


def parse_skill_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", text)
    return match.group(1).strip() if match else None


def digest_skill_dir(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(skill_dir.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(skill_dir)
        digest.update(rel.as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


class Contribution:
    def __init__(self, root_path: str, write_root: str | None, skill_dir: Path):
        self.root_path = root_path
        self.write_root = write_root
        self.skill_dir = skill_dir


def scan_root(home: Path, root_rel: str) -> dict[str, Path]:
    """One level of `<root>/<name>/SKILL.md`, matching how these tools scan a skills root."""
    found: dict[str, Path] = {}
    root = home / root_rel
    if not root.is_dir():
        return found
    for child in sorted(root.iterdir()):
        skill_md = child / "SKILL.md"
        if not child.is_dir() or not skill_md.is_file():
            continue
        name = parse_skill_name(skill_md)
        if name:
            found[name] = child
    return found


def effective_winner(dedup: str, contributions: list[Contribution]) -> tuple[str | None, str]:
    """Return (effective root_path or None, human explanation) for a name with >1 contributor."""
    if "last-scan-wins" in dedup:
        winner = contributions[-1]
        return winner.root_path, f"last-scan-wins -> {winner.root_path}"
    if "not by name" in dedup:
        return None, "not deduplicated -- shown at every contributing path simultaneously"
    if "undocumented" in dedup:
        return None, "undocumented precedence -- verify manually"
    return None, "unknown dedup rule"


def audit_agent(name: str, entry: dict, home: Path) -> tuple[list[str], bool]:
    """Return (report_lines, ok)."""
    lines: list[str] = [f"## {name}"]
    ok = True
    roots = entry.get("roots", [])
    by_skill: dict[str, list[Contribution]] = {}
    for root_entry in roots:
        root_rel = root_entry["path"]
        write_root = root_entry.get("write_root")
        found = scan_root(home, root_rel)
        for skill_name, skill_dir in found.items():
            by_skill.setdefault(skill_name, []).append(
                Contribution(root_rel, write_root, skill_dir)
            )

    lines.append(f"unique skill names visible: {len(by_skill)}")
    dedup = entry.get("dedup", "")
    duplicates = {n: c for n, c in by_skill.items() if len(c) > 1}
    if not duplicates:
        lines.append("no duplicate names.")
    for skill_name, contributions in sorted(duplicates.items()):
        paths = ", ".join(f"{c.root_path} ({c.write_root or 'unmanaged'})" for c in contributions)
        all_managed = all(c.write_root is not None for c in contributions)
        digests = {digest_skill_dir(c.skill_dir) for c in contributions}
        identical = len(digests) == 1
        if all_managed and identical:
            winner_path, explanation = effective_winner(dedup, contributions)
            lines.append(
                f"  EXPECTED overlap {skill_name!r}: {paths} -- identical content, "
                f"unavoidable given this agent's own discovery graph ({explanation})"
            )
        else:
            ok = False
            reason = "content differs across roots" if not identical else "found outside a managed write_root"
            winner_path, explanation = effective_winner(dedup, contributions)
            lines.append(
                f"  PROBLEM {skill_name!r}: {paths} -- {reason} ({explanation})"
            )

    lines.append("")
    lines.append("skill id -> effective source path:")
    for skill_name in sorted(by_skill):
        contributions = by_skill[skill_name]
        if len(contributions) == 1:
            lines.append(f"  {skill_name} -> {contributions[0].skill_dir}")
        else:
            winner_path, _ = effective_winner(dedup, contributions)
            if winner_path is not None:
                winner = next(c for c in contributions if c.root_path == winner_path)
                lines.append(f"  {skill_name} -> {winner.skill_dir}  (of {len(contributions)}, wins)")
            else:
                paths = " AND ".join(str(c.skill_dir) for c in contributions)
                lines.append(f"  {skill_name} -> UNDETERMINED: {paths}")

    return lines, ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repo_root())
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args(argv)

    manifest = load_manifest(args.source.resolve())
    discovery_graph = manifest.get("discovery_graph", {})
    retired = set(manifest.get("retired_skills", []))
    home = args.home.resolve()

    overall_ok = True
    for agent_name, entry in sorted(discovery_graph.items()):
        if agent_name == "_comment":
            continue
        lines, ok = audit_agent(agent_name, entry, home)
        for line in lines:
            print(line)
        by_skill_names = {
            n for r in entry.get("roots", []) for n in scan_root(home, r["path"])
        }
        retired_visible = sorted(by_skill_names & retired)
        if retired_visible:
            ok = False
            print(f"  PROBLEM: retired skills still visible to {agent_name}: {retired_visible}")
        status = "AUDIT_OK" if ok else "AUDIT_ERROR"
        print(f"{status}: {agent_name}")
        print()
        overall_ok = overall_ok and ok

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
