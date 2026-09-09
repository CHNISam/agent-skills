#!/usr/bin/env python3
"""Compute each agent's actual effective skill catalog from the live discovery graph.

`skill-profiles.json`'s `discovery_graph` records the directories each supported agent
really scans for skills (verified against each agent's own docs/source — see
`discovery_graph_notes.md`), not just the two roots this repository writes to. This
script walks those real directories on the current machine EXACTLY the way each agent
really does — including *recursively*, per `discovery_graph[agent]["recursive"]`, for
every agent whose own source/docs say it recurses (Codex, OpenCode, Cursor all do; only
Claude Code scans one level).

Two entirely separate things live in this file, deliberately not merged into one status:

1. `managed_gate()` — the narrow, binary check `distribute_skills.py --apply` runs on
   just the skills it placed. It answers "did this apply create an unintended duplicate
   among skills this repo manages", nothing about the rest of the machine. Pass/fail.

2. `full_audit()` (what `python scripts/audit_catalog.py` with no arguments runs) — walks
   every discovery root for every agent and classifies every duplicate name found,
   anywhere, into one of three states:
     - EXPECTED: every contributing path is a root this repo writes, content identical.
       The structurally-unavoidable Claude+Agents overlap.
     - PROBLEM: a name this repo recognizes as its own (current or retired), with
       identical content, sitting somewhere this repo does not manage — a mechanically
       fixable stale leftover. Also any retired name still visible anywhere, even alone.
     - REVIEW_REQUIRED: a duplicate this repo has no authority or confident basis to
       auto-resolve — either the name is not one agent-skills has ever shipped (i.e.
       third-party/unknown provenance content this repo must never delete), or the name
       is recognized but the content genuinely differs across paths this repo does not
       control uniformly. Never auto-fixed. Never counted as clean.
   `full_audit()`'s overall status is PROBLEM if any PROBLEM exists, else REVIEW_REQUIRED
   if any REVIEW_REQUIRED exists, else CLEAN — and CLEAN is the *only* status that exits
   0. A caller (human or agent) cannot get exit 0 while an unresolved duplicate of any
   kind remains, so "the managed gate passed" can never be silently reported as "the
   catalog is clean" — that conflation is exactly the failure this file exists to close.

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


def load_known_names(source: Path, manifest: dict) -> set[str]:
    """Every skill name agent-skills has ever shipped: current top-level skills plus
    retired_skills. This is the provenance signal for full_audit()'s REVIEW_REQUIRED
    classification -- a duplicate under a name NOT in this set is not ours to judge or
    touch, no matter how confidently its content looks like a duplicate."""
    names: set[str] = set(manifest.get("retired_skills", []))
    if source.is_dir():
        for child in sorted(source.iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file():
                names.add(child.name)
    return names


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


def is_direct_placement(home: Path, root_rel: str, skill_dir: Path) -> bool:
    """True if `skill_dir` sits exactly one level below the scanned root -- the only
    shape this repo's own distributor ever writes (`<root>/<name>/SKILL.md`). A name
    found deeper than that (e.g. nested inside a third-party plugin's own
    `<container>/<name>/SKILL.md` layout) was never placed by this repo's tooling, no
    matter how exactly its content matches -- some of this repo's own skills were
    themselves verbatim copies of an upstream source (see NOTICE), so a raw install of
    that same upstream can be byte-identical to what this repo ships or once shipped,
    without being this repo's own placement (and therefore without being this repo's
    to delete) at all."""
    return skill_dir.parent == home / root_rel


class Contribution:
    def __init__(self, root_path: str, write_root: str | None, skill_dir: Path, order: int, home: Path):
        self.root_path = root_path
        self.write_root = write_root
        self.skill_dir = skill_dir
        self.order = order  # deterministic scan-order tiebreak: (root index, path)
        self.is_direct = is_direct_placement(home, root_path, skill_dir)

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


def collect_contributions(entry: dict, home: Path) -> dict[str, list[Contribution]]:
    by_skill: dict[str, list[Contribution]] = {}
    order = 0
    for root_entry in entry.get("roots", []):
        write_root = root_entry.get("write_root")
        found = scan_root(home, root_entry["path"], recursive=entry.get("recursive", False))
        for skill_name, skill_dirs in found.items():
            for skill_dir in sorted(skill_dirs):
                by_skill.setdefault(skill_name, []).append(
                    Contribution(root_entry["path"], write_root, skill_dir, order, home)
                )
                order += 1
    return by_skill


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


# ---------------------------------------------------------------------------
# 1. managed_gate() -- binary, scoped to skills this repo just applied. This is
#    what distribute_skills.py --apply calls after SYNC_OK. It never sees or
#    reports on the rest of the machine, and it has no REVIEW_REQUIRED state:
#    a name it was asked about is, by definition, one this repo manages.
# ---------------------------------------------------------------------------


def audit_agent(name: str, entry: dict, home: Path) -> tuple[list[str], bool]:
    """Full per-agent report using the simple two-way EXPECTED/PROBLEM split. Used
    directly by managed_gate() and by tests exercising that binary behavior."""
    lines: list[str] = [f"## {name}"]
    ok = True
    by_skill = collect_contributions(entry, home)

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
            lines.append(f"  PROBLEM {skill_name!r}: {paths} -- {reason} ({explanation})")

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


def managed_gate(discovery_graph: dict, home: Path, retired: set[str], applied_names: set[str]) -> tuple[list[str], bool]:
    """Scoped completion gate: fail only on a PROBLEM among `applied_names`. Unrelated
    pre-existing machine state (someone else's skill pack, its own internal duplicate)
    never blocks a distribution that never touched it."""
    lines: list[str] = []
    overall_ok = True
    for agent_name, entry in sorted(discovery_graph.items()):
        if agent_name == "_comment":
            continue
        by_skill = {
            n: c for n, c in collect_contributions(entry, home).items() if n in applied_names
        }
        problems = []
        for n, contributions in by_skill.items():
            if len(contributions) < 2:
                continue
            all_managed = all(c.write_root is not None for c in contributions)
            digests = {digest_skill_dir(c.skill_dir) for c in contributions}
            if not (all_managed and len(digests) == 1):
                problems.append(n)
        retired_visible = sorted(set(by_skill) & retired)
        ok = not problems and not retired_visible
        agent_lines = [f"## {agent_name} (scoped to {sorted(applied_names)})"]
        if problems:
            agent_lines.append(f"  PROBLEM: unintended duplicates among applied skills: {sorted(problems)}")
        if retired_visible:
            agent_lines.append(f"  PROBLEM: retired skills among applied skills: {retired_visible}")
        if ok:
            agent_lines.append("  no unintended duplicates among applied skills.")
        agent_lines.append("AUDIT_OK" if ok else "AUDIT_ERROR" + f": {agent_name}")
        lines.extend(agent_lines)
        lines.append("")
        overall_ok = overall_ok and ok
    return lines, overall_ok


# ---------------------------------------------------------------------------
# 2. full_audit() -- the whole machine, every agent, every discovery root, with
#    three-way classification. This is the only thing that may ever report
#    CLEAN, and CLEAN requires literally zero unresolved duplicates -- a
#    third-party duplicate this repo correctly refuses to delete still forces
#    REVIEW_REQUIRED, never CLEAN. See CLEAN_ASSERTION_RULE below.
# ---------------------------------------------------------------------------

STATUS_RANK = {"CLEAN": 0, "EXPECTED": 0, "REVIEW_REQUIRED": 1, "PROBLEM": 2}


def classify_duplicate(
    skill_name: str, contributions: list[Contribution], known_names: set[str], retired: set[str]
) -> tuple[str, str]:
    direct = [c for c in contributions if c.is_direct]
    nested = [c for c in contributions if not c.is_direct]
    if skill_name in retired and direct:
        # A directly-placed retired copy is unambiguously this repo's own leftover and
        # must be removed, regardless of whether a separate, untouchable nested
        # third-party copy of the same name also happens to exist alongside it.
        return (
            "PROBLEM",
            f"a retired skill name, directly placed at {[str(c.skill_dir) for c in direct]} -- "
            "should have zero copies anywhere" + (
                f" (a further nested copy also exists at {[str(c.skill_dir) for c in nested]}; "
                "that part is not this repo's to touch)" if nested else ""
            ),
        )
    if nested:
        # At least one contributing path is nested deeper than this repo's own
        # distributor ever writes (e.g. a third-party plugin's own <container>/<name>/
        # SKILL.md). This repo has no authority to remove content it did not place,
        # no matter how the content compares -- an EXPECTED verdict would wrongly imply
        # this repo's own design accounts for the overlap, and a PROBLEM verdict would
        # wrongly imply a mechanical fix this repo can actually make.
        return (
            "REVIEW_REQUIRED",
            f"at least one contributing path ({[str(c.skill_dir) for c in nested]}) is nested "
            "inside something this repo's own tooling never wrote (a third-party plugin "
            "container, most likely) -- not this repo's to judge or delete",
        )
    all_managed = all(c.write_root is not None for c in contributions)
    digests = {digest_skill_dir(c.skill_dir) for c in contributions}
    identical = len(digests) == 1
    if all_managed and identical:
        return "EXPECTED", "identical content, every contributing path is a root this repo writes"
    if skill_name not in known_names:
        return (
            "REVIEW_REQUIRED",
            "not a name agent-skills has ever shipped (current or retired) -- third-party or "
            "unknown provenance; never auto-deleted, needs a human decision",
        )
    if not identical:
        return (
            "REVIEW_REQUIRED",
            "a name agent-skills recognizes, but content differs across contributing paths -- "
            "which version is authoritative is a decision, not something this tool guesses",
        )
    return (
        "PROBLEM",
        "a name agent-skills recognizes, identical content, sitting outside every managed "
        "write_root -- a stale leftover with a clear, mechanical fix (remove it)",
    )


def audit_agent_full(
    name: str, entry: dict, home: Path, known_names: set[str], retired: set[str]
) -> tuple[list[str], dict[str, int]]:
    lines: list[str] = [f"## {name}"]
    counts = {"EXPECTED": 0, "PROBLEM": 0, "REVIEW_REQUIRED": 0}
    by_skill = collect_contributions(entry, home)

    lines.append(f"unique skill names visible: {len(by_skill)}")
    dedup = entry.get("dedup", "")
    duplicates = {n: c for n, c in by_skill.items() if len(c) > 1}
    if not duplicates:
        lines.append("no duplicate names.")
    for skill_name, contributions in sorted(duplicates.items()):
        status, reason = classify_duplicate(skill_name, contributions, known_names, retired)
        counts[status] += 1
        paths = ", ".join(f"{c.skill_dir} ({c.write_root or 'unmanaged'})" for c in contributions)
        _, explanation = effective_winner(dedup, contributions)
        lines.append(f"  {status} {skill_name!r}: {paths} -- {reason} ({explanation})")

    # A retired name is wrong to see at all, even as a single, non-duplicated
    # occurrence (classify_duplicate above only ever sees names with 2+ contributions).
    # Same nesting rule applies: only a direct placement is this repo's to fix.
    for skill_name in sorted((set(by_skill) & retired) - set(duplicates)):
        contribution = by_skill[skill_name][0]
        if contribution.is_direct:
            counts["PROBLEM"] += 1
            lines.append(f"  PROBLEM: retired skill {skill_name!r} still directly placed at {contribution.skill_dir}")
        else:
            counts["REVIEW_REQUIRED"] += 1
            lines.append(
                f"  REVIEW_REQUIRED: retired name {skill_name!r} found nested (not this repo's own "
                f"placement shape) at {contribution.skill_dir} -- likely a third-party plugin whose "
                f"own skill happens to share this name; not auto-deleted"
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

    return lines, counts


def full_audit(discovery_graph: dict, home: Path, manifest: dict, source: Path) -> tuple[list[str], str]:
    """Returns (report_lines, overall_status) where overall_status is one of
    "CLEAN", "REVIEW_REQUIRED", "PROBLEM". Only "CLEAN" may ever be reported as
    the caller-facing success state -- see CLEAN_ASSERTION_RULE."""
    retired = set(manifest.get("retired_skills", []))
    known_names = load_known_names(source, manifest)
    lines: list[str] = []
    worst = "CLEAN"
    for agent_name, entry in sorted(discovery_graph.items()):
        if agent_name == "_comment":
            continue
        agent_lines, counts = audit_agent_full(agent_name, entry, home, known_names, retired)
        # EXPECTED duplicates (the benign, unavoidable Claude+Agents overlap) never
        # move the needle -- an agent with only EXPECTED entries, or none at all, is
        # CLEAN. Only PROBLEM and REVIEW_REQUIRED count toward a non-clean status.
        agent_status = max(
            (s for s, n in counts.items() if n > 0 and s != "EXPECTED"),
            key=lambda s: STATUS_RANK[s],
            default="CLEAN",
        )
        agent_lines.append(f"AGENT_STATUS: {agent_name} = {agent_status}")
        agent_lines.append("")
        lines.extend(agent_lines)
        if STATUS_RANK[agent_status] > STATUS_RANK[worst]:
            worst = agent_status
    return lines, worst


# CLEAN_ASSERTION_RULE: full_audit()'s overall status is CLEAN iff it found zero
# PROBLEM and zero REVIEW_REQUIRED anywhere, on any agent. The literal string
# "EFFECTIVE_SKILL_CATALOG_CLEAN" (or any equivalent claim of a fully clean
# catalog) must never be asserted -- by this script, by distribute_skills.py, or
# by an agent narrating the result -- unless full_audit()'s status is exactly
# "CLEAN". A REVIEW_REQUIRED result (e.g. a correctly-undeleted third-party
# duplicate) is a distinct, non-clean terminal state, not a variant of success.
# tests/test_audit_catalog.py::test_review_required_can_never_be_reported_as_clean
# pins this down as a regression test so a future change cannot quietly widen
# what counts as "done".


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repo_root())
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args(argv)

    source = args.source.resolve()
    manifest = load_manifest(source)
    discovery_graph = manifest.get("discovery_graph", {})
    home = args.home.resolve()

    lines, status = full_audit(discovery_graph, home, manifest, source)
    for line in lines:
        print(line)
    print(f"FULL_CATALOG_STATUS: {status}")
    return {"CLEAN": 0, "REVIEW_REQUIRED": 2, "PROBLEM": 1}[status]


if __name__ == "__main__":
    raise SystemExit(main())
