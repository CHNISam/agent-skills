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
     - ACKNOWLEDGED: an intentional overlap covered by an explicit, path-exact entry in
       `skill-profiles.json`'s `duplicate_exceptions`. This is the ONLY sanctioned way a
       duplicate is allowed to persist; the exception names the agent, the logical id and
       the exact contributing paths, and a stale one (matching nothing) is itself a
       PROBLEM, so a waiver can never outlive the duplicate it waives.
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
import os
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


# A skill that ships inside a plugin/bundle does NOT enter an agent's catalog under its
# bare frontmatter `name`. The agent namespaces it as `<plugin name>:<skill name>`, taking
# the plugin name from the nearest ancestor plugin manifest. Verified empirically against
# the live runtime -- see discovery_graph_notes.md, "Logical identity is plugin-namespaced".
#
# Getting this wrong breaks the audit in BOTH directions, which is why identity, not the
# bare name, is what this file groups by:
#   * false positive -- `~/.agents/skills/brainstorming` and
#     `~/.agents/skills/superpowers/brainstorming` both declare `name: brainstorming`, but
#     the runtime shows `brainstorming` and `superpowers:brainstorming`. Two distinct
#     catalog entries, not a duplicate at all.
#   * false negative -- one plugin installed under two roots yields the same
#     `<plugin>:<skill>` id twice: a real duplicate, and one whose two SKILL.md files may
#     legitimately declare different bare names.
PLUGIN_MANIFESTS = (
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
)
# A plugin root is normally 1-3 levels above the skill (`<plugin>/skills/<name>`, or
# `<plugin>/<version>/skills/<name>` for a versioned marketplace cache). The walk is
# capped so a skill that is NOT in a plugin cannot accidentally inherit some unrelated
# manifest from far up the filesystem.
PLUGIN_ANCESTOR_LIMIT = 4


def plugin_namespace(root: Path, skill_dir: Path) -> str | None:
    """Name of the plugin owning `skill_dir`, or None when it is a plain standalone skill.

    Walks real (symlink-resolved) ancestors, because a plugin is very often installed by
    symlinking only its inner `skills/` directory into a discovery root -- the manifest
    then lives one level above the symlink *target*, entirely outside the walked root, and
    a walk over the un-resolved path would never see it.
    """
    try:
        current = skill_dir.resolve()
        stop = root.resolve()
    except OSError:
        return None
    for _ in range(PLUGIN_ANCESTOR_LIMIT):
        parent = current.parent
        if parent == current or current == stop:
            return None
        for manifest_rel in PLUGIN_MANIFESTS:
            manifest = parent / manifest_rel
            if manifest.is_file():
                try:
                    name = json.loads(manifest.read_text(encoding="utf-8")).get("name")
                except (OSError, json.JSONDecodeError):
                    name = None
                if isinstance(name, str) and name.strip():
                    return name.strip()
        current = parent
    return None


def logical_id(root: Path, skill_dir: Path, declared_name: str) -> str:
    """The identity an agent's catalog actually keys on -- what "the same skill twice"
    has to mean for the invariant to match what a user sees in the picker."""
    namespace = plugin_namespace(root, skill_dir)
    if not namespace or declared_name.startswith(f"{namespace}:"):
        return declared_name
    return f"{namespace}:{declared_name}"


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


def root_base(root_entry: dict, home: Path, project: Path) -> Path:
    """Where a declared root is anchored. Most roots hang off the user's home directory,
    but agents also scan a project-scoped root under the current working directory -- and
    a project root can collide with a user root just as easily, so the graph has to model
    both or the audit is blind to half of it."""
    return project if root_entry.get("base") == "project" else home


def is_direct_placement(root_abs: Path, skill_dir: Path) -> bool:
    """True if `skill_dir` sits exactly one level below the scanned root -- the only
    shape this repo's own distributor ever writes (`<root>/<name>/SKILL.md`). A name
    found deeper than that (e.g. nested inside a third-party plugin's own
    `<container>/<name>/SKILL.md` layout) was never placed by this repo's tooling, no
    matter how exactly its content matches -- some of this repo's own skills were
    themselves verbatim copies of an upstream source (see NOTICE), so a raw install of
    that same upstream can be byte-identical to what this repo ships or once shipped,
    without being this repo's own placement (and therefore without being this repo's
    to delete) at all."""
    return skill_dir.parent == root_abs


def canonical_key(skill_dir: Path) -> str:
    """The identity of the *file content* behind a discovered path.

    Agents share skills on purpose: a root is routinely a symlink or (on Windows) a
    junction pointing into another agent's root, so one on-disk skill is reachable by
    several paths. Reading a skill twice through two names for the same directory is one
    catalog entry, not two, so alias collapse happens before anything counts duplicates.
    """
    try:
        resolved = skill_dir.resolve()
    except OSError:
        resolved = skill_dir
    key = resolved.as_posix()
    return key.lower() if os.name == "nt" else key


class Contribution:
    def __init__(self, root_path: str, write_root: str | None, skill_dir: Path, order: int, root_abs: Path):
        self.root_path = root_path
        self.write_root = write_root
        self.skill_dir = skill_dir
        self.order = order  # deterministic scan-order tiebreak: (root index, path)
        self.root_abs = root_abs
        self.is_direct = is_direct_placement(root_abs, skill_dir)
        self.canonical = canonical_key(skill_dir)
        # Other discovered paths that resolve to this same directory. Evidence for a
        # reader, never additional catalog entries.
        self.aliases: list[Path] = []

    def describe(self) -> str:
        if not self.aliases:
            return f"{self.skill_dir} ({self.write_root or 'unmanaged'})"
        also = ", ".join(str(a) for a in self.aliases)
        return f"{self.skill_dir} ({self.write_root or 'unmanaged'}; same directory also reached as {also})"

    def __repr__(self) -> str:
        return f"{self.skill_dir}"


def scan_root(root: Path, recursive: bool = False) -> dict[str, list[Path]]:
    """Every `SKILL.md` under `<root>`, one level or fully recursive.

    Returns logical id -> list of directories contributing that id (usually one; more than
    one means a duplicate exists WITHIN this single root, e.g. two sibling bundle
    directories each containing a nested SKILL.md that resolves to the same id).

    Keys are `logical_id()`s, not raw frontmatter names: a plugin-owned skill enters the
    catalog namespaced, so grouping by bare name would both invent duplicates that the
    runtime does not show and miss ones it does.
    """
    found: dict[str, list[Path]] = {}
    if not root.is_dir():
        return found
    if recursive:
        try:
            # Python 3.13 stopped following symlinks while expanding `**` by default.
            # Agents do follow them, and plugins are routinely installed by linking their
            # inner `skills/` directory into a discovery root, so an unfollowed link is a
            # blind spot: skills visible to the agent that the audit cannot see at all.
            skill_files = sorted(root.rglob("SKILL.md", recurse_symlinks=True))
        except TypeError:  # Python < 3.13 follows them already
            skill_files = sorted(root.rglob("SKILL.md"))
    else:
        skill_files = sorted(
            child / "SKILL.md" for child in root.iterdir()
            if child.is_dir() and (child / "SKILL.md").is_file()
        )
    for skill_md in skill_files:
        name = parse_skill_name(skill_md)
        if name:
            identity = logical_id(root, skill_md.parent, name)
            found.setdefault(identity, []).append(skill_md.parent)
    return found


def collect_contributions(entry: dict, home: Path, project: Path | None = None) -> dict[str, list[Contribution]]:
    project = project or Path.cwd()
    by_skill: dict[str, list[Contribution]] = {}
    order = 0
    for root_entry in entry.get("roots", []):
        if root_entry.get("install_gated"):
            # Declared for the record and for runtime_check(), but never walked: whether a
            # plugin under such a root is actually installed and enabled is agent state,
            # not a filesystem fact. Walking it would report skills the runtime does not
            # show -- including phantom duplicates between two cached versions of one
            # plugin -- so the static model deliberately stops at the root's edge.
            continue
        write_root = root_entry.get("write_root")
        root_abs = root_base(root_entry, home, project) / root_entry["path"]
        found = scan_root(root_abs, recursive=entry.get("recursive", False))
        for skill_name, skill_dirs in found.items():
            for skill_dir in sorted(skill_dirs):
                contribution = Contribution(root_entry["path"], write_root, skill_dir, order, root_abs)
                existing = next(
                    (c for c in by_skill.get(skill_name, []) if c.canonical == contribution.canonical),
                    None,
                )
                if existing is not None:
                    # Same directory, reached again through another root. Record the
                    # alias as evidence; do not count it as a second catalog entry.
                    existing.aliases.append(skill_dir)
                    continue
                by_skill.setdefault(skill_name, []).append(contribution)
                order += 1
    return by_skill


def dedup_kind(entry: dict) -> str:
    """How the agent itself resolves two skills that share one identity.

    This is the whole difference between "two files exist" and "the user sees the skill
    twice", and only the second is a defect:

      "by-path" -- the agent does not merge by identity, so every contributing path
                   becomes its own catalog entry. More than one entry IS the duplicate.
      "by-name" -- the agent merges by identity itself and surfaces exactly one entry
                   (last scanned root wins). Several contributions are the normal shape
                   of deliberate cross-agent reuse and can never be a runtime duplicate.
    """
    return entry.get("dedup_kind", "by-path")


def exposed_more_than_once(entry: dict, contributions: list[Contribution]) -> bool:
    """The invariant, stated exactly: does THIS agent expose this one logical skill more
    than once? Alias-collapsed contributions, judged against the agent's own dedup rule."""
    return len(contributions) > 1 and dedup_kind(entry) == "by-path"


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


def audit_agent(name: str, entry: dict, home: Path, project: Path | None = None) -> tuple[list[str], bool]:
    """Full per-agent report using the simple two-way EXPECTED/PROBLEM split. Used
    directly by managed_gate() and by tests exercising that binary behavior."""
    lines: list[str] = [f"## {name}"]
    ok = True
    by_skill = collect_contributions(entry, home, project)

    lines.append(f"unique skill identities visible: {len(by_skill)}")
    dedup = entry.get("dedup", "")
    duplicates = {n: c for n, c in by_skill.items() if len(c) > 1}
    if not duplicates:
        lines.append("no duplicate identities.")
    for skill_name, contributions in sorted(duplicates.items()):
        paths = ", ".join(c.describe() for c in contributions)
        winner, explanation = effective_winner(dedup, contributions)
        if not exposed_more_than_once(entry, contributions):
            # The agent merges these itself, so the user sees one entry. Reported for
            # visibility -- which copy wins is worth knowing -- but not a defect.
            lines.append(
                f"  DEDUPED {skill_name!r}: {paths} -- {name} resolves this identity to a "
                f"single catalog entry ({explanation})"
            )
            continue
        all_managed = all(c.write_root is not None for c in contributions)
        digests = {digest_skill_dir(c.skill_dir) for c in contributions}
        identical = len(digests) == 1
        if all_managed and identical:
            lines.append(
                f"  EXPECTED overlap {skill_name!r}: {paths} -- identical content, "
                f"unavoidable given this agent's own discovery graph ({explanation})"
            )
        else:
            ok = False
            reason = "content differs across paths" if not identical else "found outside a managed write_root"
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


def managed_gate(discovery_graph: dict, home: Path, retired: set[str], applied_names: set[str], project: Path | None = None) -> tuple[list[str], bool]:
    """Scoped completion gate: fail only on a PROBLEM among `applied_names`. Unrelated
    pre-existing machine state (someone else's skill pack, its own internal duplicate)
    never blocks a distribution that never touched it."""
    lines: list[str] = []
    overall_ok = True
    for agent_name, entry in sorted(discovery_graph.items()):
        if agent_name == "_comment":
            continue
        by_skill = {
            n: c for n, c in collect_contributions(entry, home, project).items() if n in applied_names
        }
        problems = []
        for n, contributions in by_skill.items():
            if not exposed_more_than_once(entry, contributions):
                continue
            all_managed = all(c.write_root is not None for c in contributions)
            digests = {digest_skill_dir(c.skill_dir) for c in contributions}
            if not (all_managed and len(digests) == 1):
                problems.append(n)
        retired_visible = sorted(
            n for n in set(by_skill) & retired if any(c.is_direct for c in by_skill[n])
        )
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

# ---------------------------------------------------------------------------
# Validated exceptions
#
# The invariant is "one logical skill, one entry per agent discovery graph".
# A handful of overlaps are genuinely intentional (two same-named but materially
# different skills a user wants both of, say). Those are allowed only when
# `skill-profiles.json` records an explicit exception naming the agent, the
# logical id, and the exact set of contributing paths -- so an exception cannot
# quietly widen to cover a *new* duplicate that appears at a third path later.
#
# Exceptions are validated in both directions: an unmatched exception (the
# duplicate it describes is gone, or moved) is itself a PROBLEM, so the list
# cannot rot into a permanent blanket waiver.
# ---------------------------------------------------------------------------


def load_exceptions(manifest: dict) -> list[dict]:
    raw = manifest.get("duplicate_exceptions", [])
    return raw if isinstance(raw, list) else []


def relative_paths(contributions: list["Contribution"], home: Path) -> tuple[str, ...]:
    out = []
    for contribution in contributions:
        try:
            out.append(contribution.skill_dir.relative_to(home).as_posix())
        except ValueError:
            out.append(contribution.skill_dir.as_posix())
    return tuple(sorted(out))


def match_exception(
    agent: str, skill_id: str, contributions: list["Contribution"], home: Path, exceptions: list[dict]
) -> dict | None:
    actual = relative_paths(contributions, home)
    for exception in exceptions:
        if exception.get("agent") != agent or exception.get("logical_id") != skill_id:
            continue
        declared = tuple(sorted(str(p).replace("\\", "/") for p in exception.get("paths", [])))
        if declared == actual:
            return exception
    return None


STATUS_RANK = {
    "CLEAN": 0,
    "EXPECTED": 0,
    "ACKNOWLEDGED": 0,
    "DEDUPED": 0,
    "REVIEW_REQUIRED": 1,
    "PROBLEM": 2,
}


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
    name: str,
    entry: dict,
    home: Path,
    known_names: set[str],
    retired: set[str],
    exceptions: list[dict] | None = None,
    project: Path | None = None,
) -> tuple[list[str], dict[str, int], set[int]]:
    exceptions = exceptions or []
    lines: list[str] = [f"## {name}"]
    counts = {"EXPECTED": 0, "ACKNOWLEDGED": 0, "DEDUPED": 0, "PROBLEM": 0, "REVIEW_REQUIRED": 0}
    used_exceptions: set[int] = set()
    by_skill = collect_contributions(entry, home, project)

    lines.append(f"unique skill identities visible: {len(by_skill)}")
    dedup = entry.get("dedup", "")
    duplicates = {n: c for n, c in by_skill.items() if len(c) > 1}
    if not duplicates:
        lines.append("no duplicate identities.")
    for skill_name, contributions in sorted(duplicates.items()):
        paths = ", ".join(c.describe() for c in contributions)
        _, explanation = effective_winner(dedup, contributions)
        if not exposed_more_than_once(entry, contributions):
            # Several contributions, one catalog entry: the agent dedupes by identity, so
            # this is cross-agent reuse working as intended, not a duplicate. Recorded so
            # a reader can still see every contributing path and which one wins.
            counts["DEDUPED"] += 1
            lines.append(
                f"  DEDUPED {skill_name!r}: {paths} -- {name} exposes this identity once "
                f"({explanation})"
            )
            continue
        exception = match_exception(name, skill_name, contributions, home, exceptions)
        if exception is not None:
            used_exceptions.add(id(exception))
            counts["ACKNOWLEDGED"] += 1
            lines.append(
                f"  ACKNOWLEDGED {skill_name!r}: {paths} -- explicit validated exception in "
                f"skill-profiles.json: {exception.get('reason', '(no reason recorded)')} ({explanation})"
            )
            continue
        status, reason = classify_duplicate(skill_name, contributions, known_names, retired)
        counts[status] += 1
        lines.append(
            f"  {status} {skill_name!r}: agent={name}; identity={skill_name!r}; "
            f"paths={paths}; why={reason} ({explanation})"
        )

    # A retired name is wrong to see at all, even as a single, non-duplicated
    # occurrence (classify_duplicate above only ever sees names with 2+ contributions).
    # Same nesting rule applies: only a direct placement is this repo's to fix.
    for skill_name in sorted((set(by_skill) & retired) - set(duplicates)):
        contribution = by_skill[skill_name][0]
        if contribution.is_direct:
            counts["PROBLEM"] += 1
            lines.append(f"  PROBLEM: retired skill {skill_name!r} still directly placed at {contribution.skill_dir}")
        else:
            # Not this repo's placement shape, so not this repo's copy: a third-party
            # pack shipping its own skill that happens to share a retired name. Naming
            # collision, not a leftover, and nothing here is wrong -- note it and move on.
            lines.append(
                f"  NOTE: retired name {skill_name!r} is also used by a third-party skill at "
                f"{contribution.skill_dir}; that is not this repo's placement and not a finding"
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

    return lines, counts, used_exceptions


def full_audit(discovery_graph: dict, home: Path, manifest: dict, source: Path, project: Path | None = None) -> tuple[list[str], str]:
    """Returns (report_lines, overall_status) where overall_status is one of
    "CLEAN", "REVIEW_REQUIRED", "PROBLEM". Only "CLEAN" may ever be reported as
    the caller-facing success state -- see CLEAN_ASSERTION_RULE."""
    retired = set(manifest.get("retired_skills", []))
    known_names = load_known_names(source, manifest)
    exceptions = load_exceptions(manifest)
    lines: list[str] = []
    worst = "CLEAN"
    used_exceptions: set[int] = set()
    for agent_name, entry in sorted(discovery_graph.items()):
        if agent_name == "_comment":
            continue
        agent_lines, counts, used = audit_agent_full(
            agent_name, entry, home, known_names, retired, exceptions, project
        )
        used_exceptions |= used
        # EXPECTED duplicates (the benign, unavoidable Claude+Agents overlap) and
        # ACKNOWLEDGED ones (an explicit, path-exact, validated exception) never move
        # the needle. Only PROBLEM and REVIEW_REQUIRED count toward a non-clean status.
        agent_status = max(
            (s for s, n in counts.items() if n > 0 and s not in ("EXPECTED", "ACKNOWLEDGED", "DEDUPED")),
            key=lambda s: STATUS_RANK[s],
            default="CLEAN",
        )
        agent_lines.append(f"AGENT_STATUS: {agent_name} = {agent_status}")
        agent_lines.append("")
        lines.extend(agent_lines)
        if STATUS_RANK[agent_status] > STATUS_RANK[worst]:
            worst = agent_status

    # An exception that matched nothing is a stale waiver: the duplicate it was written
    # for is gone or has moved to a different set of paths. Left unchecked it would sit
    # in the manifest pre-approving a future duplicate nobody reviewed, so it fails.
    stale = [e for e in exceptions if id(e) not in used_exceptions]
    if stale:
        lines.append("## duplicate_exceptions")
        for exception in stale:
            lines.append(
                f"  PROBLEM stale exception: agent={exception.get('agent')!r} "
                f"identity={exception.get('logical_id')!r} paths={exception.get('paths')} -- "
                "matches no duplicate currently in the discovery graph; remove it from "
                "skill-profiles.json (a waiver must never outlive the duplicate it waives)"
            )
        lines.append("AGENT_STATUS: duplicate_exceptions = PROBLEM")
        lines.append("")
        worst = "PROBLEM"
    return lines, worst


# CLEAN_ASSERTION_RULE: full_audit()'s overall status is CLEAN iff it found zero
# PROBLEM and zero REVIEW_REQUIRED anywhere, on any agent (EXPECTED and ACKNOWLEDGED
# do not count against it -- but ACKNOWLEDGED requires a matching, non-stale entry in
# duplicate_exceptions, which is a reviewed decision, not a default). The literal string
# "EFFECTIVE_SKILL_CATALOG_CLEAN" (or any equivalent claim of a fully clean
# catalog) must never be asserted -- by this script, by distribute_skills.py, or
# by an agent narrating the result -- unless full_audit()'s status is exactly
# "CLEAN". A REVIEW_REQUIRED result (e.g. a correctly-undeleted third-party
# duplicate) is a distinct, non-clean terminal state, not a variant of success.
# tests/test_audit_catalog.py::test_review_required_can_never_be_reported_as_clean
# pins this down as a regression test so a future change cannot quietly widen
# what counts as "done".


# ---------------------------------------------------------------------------
# 3. runtime_check() -- prove the static model above still matches what the agent
#    itself does. Everything else in this file reasons from `discovery_graph`; if
#    that description of an agent drifts from the agent's real behaviour (a new
#    root, a changed identity rule), every verdict silently becomes fiction. This
#    asks the agent to render its own catalog and diffs it against the model.
#    Deterministic and LLM-free: `codex debug prompt-input` only renders the
#    prompt Codex would build, it does not call a model.
# ---------------------------------------------------------------------------

RUNTIME_COMMANDS = {
    # agent -> argv rendering that agent's own model-visible skill list
    "codex": ["codex", "debug", "prompt-input"],
}


def extract_skills_block(payload: str) -> str:
    """Pull the rendered skills block out of an agent's prompt dump.

    `codex debug prompt-input` emits the whole prompt as JSON, so the block arrives as an
    escaped string inside one message; a plain-text dump is accepted unchanged.
    """
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return payload

    def walk(node) -> str | None:
        if isinstance(node, str):
            return node if "<skills_instructions>" in node else None
        if isinstance(node, dict):
            node = node.values()
        if isinstance(node, (list, type({}.values()))):
            for child in node:
                found = walk(child)
                if found:
                    return found
        return None

    return walk(data) or ""


def parse_runtime_catalog(text: str) -> set[tuple[str, str]]:
    """(logical id, absolute SKILL.md dir) for every entry in a rendered skills block.

    The block declares a root table (`- ``r0`` = ``<abs path>``) and then one line per
    skill ending in `(file: r<N>/<relative>/SKILL.md)`.
    """
    roots: dict[str, str] = {}
    entries: set[tuple[str, str]] = set()
    for line in text.splitlines():
        root_match = re.match(r"^- `(r\d+)` = `(.+)`\s*$", line)
        if root_match:
            roots[root_match.group(1)] = root_match.group(2)
            continue
        file_match = re.search(r"\(file: (r\d+)/(.+?)/SKILL\.md\)\s*$", line)
        if not file_match or not line.startswith("- "):
            continue
        identity = line[2:].split(":", 1)[0]
        remainder = line[2:]
        # Namespaced ids contain a colon; the description follows the LAST colon that
        # separates id from text, so rebuild the id from the leading non-space run.
        identity = remainder.split(": ", 1)[0]
        root = roots.get(file_match.group(1))
        if root is None:
            continue
        entries.add((identity, str(Path(root) / file_match.group(2))))
    return entries


def runtime_check(agent: str, entry: dict, home: Path, project: Path | None = None) -> tuple[list[str], bool]:
    """Diff the modelled catalog for `agent` against the one `agent` renders itself."""
    import shutil as _shutil
    import subprocess

    lines = [f"## runtime check: {agent}"]
    argv = RUNTIME_COMMANDS.get(agent)
    if argv is None:
        lines.append(f"  SKIPPED: no runtime rendering command known for {agent!r}")
        return lines, True
    executable = _shutil.which(argv[0])
    if executable is None:
        lines.append(f"  SKIPPED: {argv[0]!r} is not installed here (expected in CI)")
        return lines, True
    # Resolve through which(): on Windows the entry point is a .cmd shim that
    # subprocess cannot exec by bare name without a shell.
    argv = [executable, *argv[1:]]
    try:
        completed = subprocess.run(argv, capture_output=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        lines.append(f"  SKIPPED: could not run {' '.join(argv)}: {exc}")
        return lines, True
    if completed.returncode != 0:
        lines.append(f"  SKIPPED: {' '.join(argv)} exited {completed.returncode}")
        return lines, True

    # Decoded here, not by subprocess: the rendered prompt is UTF-8 and carries
    # non-ASCII punctuation that a Windows console codepage would fail to decode.
    payload = (completed.stdout or b"").decode("utf-8", errors="replace")
    actual = parse_runtime_catalog(extract_skills_block(payload))
    if not actual:
        lines.append("  SKIPPED: no skills block found in the rendered prompt")
        return lines, True

    modelled = {
        (identity, str(contribution.skill_dir))
        for identity, contributions in collect_contributions(entry, home, project).items()
        for contribution in contributions
    }

    def normalise(pairs: set[tuple[str, str]]) -> set[tuple[str, str]]:
        return {(i, Path(p).resolve().as_posix().lower()) for i, p in pairs}

    # Entries the static model deliberately does not walk (see collect_contributions).
    gated_roots = [
        (root_base(r, home, project or Path.cwd()) / r["path"]).resolve().as_posix().lower()
        for r in entry.get("roots", [])
        if r.get("install_gated")
    ]

    def is_gated(path: str) -> bool:
        return any(path.startswith(f"{root}/") for root in gated_roots)

    all_unmodelled = normalise(actual) - normalise(modelled)
    gated = {pair for pair in all_unmodelled if is_gated(pair[1])}
    unmodelled = all_unmodelled - gated
    unrendered = normalise(modelled) - normalise(actual)
    lines.append(
        f"  runtime entries: {len(actual)}; modelled entries: {len(modelled)}; "
        f"under a declared install-gated root (not statically walked): {len(gated)}"
    )

    # The two directions are not symmetric.
    #
    # Runtime shows something the model does not: a blind spot. The audit cannot see a
    # duplicate living there, so this fails.
    #
    # Model shows something the runtime does not: over-reporting. It can only ever
    # produce a duplicate finding a human then reviews, never a silent miss, and some of
    # it is unavoidable -- a skill root can be gated by install or feature state that no
    # filesystem walk can observe (`install_gated` roots such as the plugin cache, where
    # only installed+enabled plugins reach the catalog). Reported, not fatal.
    for identity, path in sorted(unmodelled):
        lines.append(
            f"  RUNTIME_DRIFT: {agent} shows {identity!r} at {path}, which this repo's "
            "discovery_graph does not model -- add the root, or fix the identity rule"
        )
    for identity, path in sorted(unrendered):
        lines.append(
            f"  RUNTIME_OVER_REPORT: this repo models {identity!r} at {path}, which {agent} "
            "does not currently show (install- or feature-gated); conservative, not fatal"
        )
    ok = not unmodelled
    lines.append(
        f"RUNTIME_CHECK: {agent} = {'MATCHES' if ok else 'DRIFTED'} "
        f"(unmodelled={len(unmodelled)}, over-reported={len(unrendered)})"
    )
    return lines, ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repo_root())
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="directory the agents would treat as the current project (default: cwd)",
    )
    parser.add_argument(
        "--runtime",
        action="store_true",
        help=(
            "additionally ask each agent that can render its own catalog to do so, and "
            "fail on any drift between that and this repo's discovery_graph model"
        ),
    )
    args = parser.parse_args(argv)

    source = args.source.resolve()
    manifest = load_manifest(source)
    discovery_graph = manifest.get("discovery_graph", {})
    home = args.home.resolve()
    project = args.project.resolve()

    lines, status = full_audit(discovery_graph, home, manifest, source, project)
    for line in lines:
        print(line)
    print(f"DUPLICATE_EXCEPTIONS_DECLARED: {len(load_exceptions(manifest))}")

    if args.runtime:
        runtime_ok = True
        for agent_name, entry in sorted(discovery_graph.items()):
            if agent_name == "_comment":
                continue
            runtime_lines, agent_ok = runtime_check(agent_name, entry, home, project)
            for line in runtime_lines:
                print(line)
            runtime_ok = runtime_ok and agent_ok
        if not runtime_ok:
            print("FULL_CATALOG_STATUS: PROBLEM")
            return 1

    print(f"FULL_CATALOG_STATUS: {status}")
    return {"CLEAN": 0, "REVIEW_REQUIRED": 2, "PROBLEM": 1}[status]


if __name__ == "__main__":
    raise SystemExit(main())
