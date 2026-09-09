#!/usr/bin/env python3
"""Compute each agent's actual effective skill catalog from the live discovery graph.

`skill-profiles.json`'s `discovery_graph` records the directories each supported agent
really scans for skills (verified against each agent's own docs/source — see
`discovery_graph_notes.md`), not just the two roots this repository writes to. This
script walks those real directories on the current machine EXACTLY the way each agent
really does — including *recursively*, per `discovery_graph[agent]["recursive"]`, for
every agent whose own source/docs say it recurses (Codex, OpenCode, Cursor all do; only
Claude Code scans one level). A one-level-only scanner cannot see a duplicate made of two
sibling directories nested inside the SAME root (e.g. an old skill-pack install sitting
next to its own reinstall under a renamed folder) — that pattern is real and has been
observed on real machines; see `discovery_graph_notes.md`'s "Escaped regression" section.

It reports what each agent would actually see: total unique skills, any name found at
more than one effective path, and which of those are the *expected* Claude+Agents overlap
this repo's design can't remove (both writable roots, identical content) versus a
*problem* (a name reachable from a root this repo does not manage, two different contents
under one name, or a retired name still visible) that indicates leftover/stale placement.

Read-only. Never writes anything. `main()`'s exit code is the completion gate:
`distribute_skills.py --apply` calls it after a successful sync and fails the run if any
PROBLEM is found among the skills it just placed — distribution success is defined as
"the effective catalog is clean", not "files copied and SYNC_OK printed".
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
    def __init__(self, root_path: str, write_root: str | None, skill_dir: Path, order: int):
        self.root_path = root_path
        self.write_root = write_root
        self.skill_dir = skill_dir
        self.order = order  # deterministic scan-order tiebreak: (root index, path)

    def __repr__(self) -> str:
        return f"{self.skill_dir}"


def scan_root(home: Path, root_rel: str, recursive: bool = False) -> dict[str, list[Path]]:
    """Every `SKILL.md` under `<root>`, one level or fully recursive.

    Returns name -> list of directories declaring that name (usually one; more than one
    means a same-name duplicate exists WITHIN this single root, e.g. two sibling
    directories both containing a nested SKILL.md with the same declared name).
    """
    found: dict[str, list[Path]] = {}
    root = home / root_rel
    if not root.is_dir():
        return found
    if recursive:
        skill_files = sorted(root.rglob("SKILL.md"))
    else:
        skill_files = sorted(
            child / "SKILL.md" for child in root.iterdir()
            if child.is_dir() and (child / "SKILL.md").is_file()
        )
    for skill_md in skill_files:
        name = parse_skill_name(skill_md)
        if name:
            found.setdefault(name, []).append(skill_md.parent)
    return found


def effective_winner(dedup: str, contributions: list[Contribution]) -> tuple[Contribution | None, str]:
    """Return (winning Contribution or None, human explanation) for a name with >1 contributor."""
    ordered = sorted(contributions, key=lambda c: c.order)
    if "last-scan-wins" in dedup:
        winner = ordered[-1]
        return winner, f"last-scan-wins -> {winner.skill_dir}"
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
    recursive = entry.get("recursive", False)
    by_skill: dict[str, list[Contribution]] = {}
    order = 0
    for root_entry in roots:
        root_rel = root_entry["path"]
        write_root = root_entry.get("write_root")
        found = scan_root(home, root_rel, recursive=recursive)
        for skill_name, skill_dirs in found.items():
            for skill_dir in sorted(skill_dirs):
                by_skill.setdefault(skill_name, []).append(
                    Contribution(root_rel, write_root, skill_dir, order)
                )
                order += 1

    lines.append(f"unique skill names visible: {len(by_skill)}")
    dedup = entry.get("dedup", "")
    duplicates = {n: c for n, c in by_skill.items() if len(c) > 1}
    if not duplicates:
        lines.append("no duplicate names.")
    for skill_name, contributions in sorted(duplicates.items()):
        paths = ", ".join(f"{c.skill_dir} ({c.write_root or 'unmanaged'})" for c in contributions)
        all_managed = all(c.write_root is not None for c in contributions)
        digests = {digest_skill_dir(c.skill_dir) for c in contributions}
        identical = len(digests) == 1
        if all_managed and identical:
            winner, explanation = effective_winner(dedup, contributions)
            lines.append(
                f"  EXPECTED overlap {skill_name!r}: {paths} -- identical content, "
                f"unavoidable given this agent's own discovery graph ({explanation})"
            )
        else:
            ok = False
            reason = "content differs across paths" if not identical else "found outside a managed write_root"
            winner, explanation = effective_winner(dedup, contributions)
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
            winner, _ = effective_winner(dedup, contributions)
            if winner is not None:
                lines.append(f"  {skill_name} -> {winner.skill_dir}  (of {len(contributions)}, wins)")
            else:
                paths = " AND ".join(str(c.skill_dir) for c in contributions)
                lines.append(f"  {skill_name} -> UNDETERMINED: {paths}")

    return lines, ok


def audit_names(discovery_graph: dict, home: Path, retired: set[str], only_names: set[str] | None = None) -> tuple[list[str], bool]:
    """Run the full audit; if `only_names` is given, report/gate on only those skill names
    (used by the distribute_skills.py completion gate to check just what it applied,
    without failing on unrelated pre-existing machine state it did not touch)."""
    lines: list[str] = []
    overall_ok = True
    for agent_name, entry in sorted(discovery_graph.items()):
        if agent_name == "_comment":
            continue
        agent_lines, ok = audit_agent(agent_name, entry, home)
        if only_names is not None:
            # Re-filter: only fail/report on the names we were asked about.
            roots = entry.get("roots", [])
            recursive = entry.get("recursive", False)
            by_skill: dict[str, list[Path]] = {}
            for root_entry in roots:
                found = scan_root(home, root_entry["path"], recursive=recursive)
                for n, dirs in found.items():
                    if n in only_names:
                        by_skill.setdefault(n, []).extend(dirs)
            problems = []
            for n, dirs in by_skill.items():
                if len(dirs) < 2:
                    continue
                write_roots = []
                for root_entry in roots:
                    found = scan_root(home, root_entry["path"], recursive=recursive)
                    if n in found:
                        write_roots.append(root_entry.get("write_root"))
                digests = {digest_skill_dir(d) for d in dirs}
                if not (all(w is not None for w in write_roots) and len(digests) == 1):
                    problems.append(n)
            ok = not problems
            agent_lines = [f"## {agent_name} (scoped to {sorted(only_names)})"]
            if problems:
                agent_lines.append(f"  PROBLEM: unintended duplicates among applied skills: {sorted(problems)}")
            else:
                agent_lines.append("  no unintended duplicates among applied skills.")
        lines.extend(agent_lines)
        by_skill_names = {
            n for r in entry.get("roots", [])
            for n in scan_root(home, r["path"], recursive=entry.get("recursive", False))
        }
        checked = by_skill_names if only_names is None else (by_skill_names & only_names)
        retired_visible = sorted(checked & retired)
        if retired_visible:
            ok = False
            lines.append(f"  PROBLEM: retired skills still visible to {agent_name}: {retired_visible}")
        status = "AUDIT_OK" if ok else "AUDIT_ERROR"
        lines.append(f"{status}: {agent_name}")
        lines.append("")
        overall_ok = overall_ok and ok
    return lines, overall_ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repo_root())
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args(argv)

    manifest = load_manifest(args.source.resolve())
    discovery_graph = manifest.get("discovery_graph", {})
    retired = set(manifest.get("retired_skills", []))
    home = args.home.resolve()

    lines, ok = audit_names(discovery_graph, home, retired)
    for line in lines:
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
