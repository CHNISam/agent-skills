import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_catalog.py"
SPEC = importlib.util.spec_from_file_location("audit_catalog", SCRIPT)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def write_skill(root: Path, name: str, body: str = "content") -> None:
    folder = root / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test {name}\n---\n\n{body}\n",
        encoding="utf-8",
    )


class AuditCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_no_overlap_is_clean(self):
        # A skill placed at exactly one root, on a two-root agent: no duplicate,
        # no problem -- the ordinary case for the vast majority of skills.
        write_skill(self.home / ".claude" / "skills", "git-workflow")
        entry = {
            "roots": [
                {"path": ".claude/skills", "write_root": "claude"},
                {"path": ".agents/skills", "write_root": "agents"},
            ],
            "dedup": "by name, last-scan-wins, logs a warning on collision",
        }
        lines, ok = audit.audit_agent("opencode", entry, self.home)
        self.assertTrue(ok)
        self.assertTrue(any("no duplicate names" in line for line in lines))

    def test_identical_content_at_two_managed_roots_is_expected_not_a_problem(self):
        # This is the structurally-unavoidable Claude+Agents overlap every
        # OpenCode/Cursor-shaped agent has by design: same content, both roots
        # are ones this repo writes (write_root is not None). Must not fail.
        write_skill(self.home / ".claude" / "skills", "git-workflow", body="X")
        write_skill(self.home / ".agents" / "skills", "git-workflow", body="X")
        entry = {
            "roots": [
                {"path": ".claude/skills", "write_root": "claude"},
                {"path": ".agents/skills", "write_root": "agents"},
            ],
            "dedup": "by name, last-scan-wins, logs a warning on collision",
        }
        lines, ok = audit.audit_agent("opencode", entry, self.home)
        self.assertTrue(ok, "\n".join(lines))
        self.assertTrue(any("EXPECTED overlap" in line for line in lines))
        # last-scan-wins: .agents/skills is listed after .claude/skills, so it wins.
        winner_line = next(line for line in lines if line.strip().startswith("git-workflow ->"))
        self.assertIn(str(self.home / ".agents" / "skills" / "git-workflow"), winner_line)

    def test_duplicate_id_at_an_unmanaged_root_is_a_problem(self):
        # This is the actual bug this whole task exists to catch: the same
        # skill id reachable from a root this repo does NOT write (write_root
        # is None) -- e.g. stale content left behind in a decommissioned root.
        write_skill(self.home / ".agents" / "skills", "git-workflow")
        write_skill(self.home / ".codex" / "skills", "git-workflow")
        entry = {
            "roots": [
                {"path": ".agents/skills", "write_root": "agents"},
                {"path": ".codex/skills", "write_root": None},
            ],
            "dedup": "by-path, not by name: a same-name skill present at two roots is shown twice, unmerged",
        }
        lines, ok = audit.audit_agent("codex", entry, self.home)
        self.assertFalse(ok)
        self.assertTrue(any("PROBLEM" in line and "git-workflow" in line for line in lines))

    def test_duplicate_id_with_different_content_is_a_problem_even_if_both_managed(self):
        # Same name, both roots are ones this repo writes, but the content
        # actually differs -- a real conflict (e.g. only one root got refreshed),
        # not the benign synced-copy overlap.
        write_skill(self.home / ".claude" / "skills", "git-workflow", body="old")
        write_skill(self.home / ".agents" / "skills", "git-workflow", body="new")
        entry = {
            "roots": [
                {"path": ".claude/skills", "write_root": "claude"},
                {"path": ".agents/skills", "write_root": "agents"},
            ],
            "dedup": "by name, last-scan-wins, logs a warning on collision",
        }
        lines, ok = audit.audit_agent("opencode", entry, self.home)
        self.assertFalse(ok)
        self.assertTrue(any("content differs" in line for line in lines))

    def test_unmanaged_personal_skill_at_a_single_root_is_never_flagged(self):
        # A personal skill that only exists at one root is completely normal
        # and must never be reported as a problem, duplicate, or otherwise.
        write_skill(self.home / ".claude" / "skills", "my-personal-thing")
        entry = {
            "roots": [
                {"path": ".claude/skills", "write_root": "claude"},
                {"path": ".agents/skills", "write_root": "agents"},
            ],
            "dedup": "by name, last-scan-wins, logs a warning on collision",
        }
        lines, ok = audit.audit_agent("opencode", entry, self.home)
        self.assertTrue(ok)
        self.assertFalse(any("my-personal-thing" in line and "PROBLEM" in line for line in lines))

    def test_retired_skill_still_visible_is_flagged_by_main(self):
        write_skill(self.home / ".agents" / "skills", "preventing-repeat-failures")
        source = self.home / "source"
        source.mkdir()
        (source / "skill-profiles.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "profiles": {"core": []},
                    "targets": {"agents": ".agents/skills"},
                    "discovery_graph": {
                        "codex": {
                            "roots": [{"path": ".agents/skills", "write_root": "agents"}],
                            "dedup": "by-path, not by name",
                        }
                    },
                    "retired_skills": ["preventing-repeat-failures"],
                }
            ),
            encoding="utf-8",
        )
        exit_code = audit.main(["--source", str(source), "--home", str(self.home)])
        self.assertEqual(exit_code, 1)

    def test_byte_identical_copies_at_two_unmanaged_roots_is_still_a_problem(self):
        # Identical content is only EXPECTED when every contributing root is one
        # this repo writes (write_root is not None). Two unmanaged roots with
        # identical content is not a benign synced overlap -- it's exactly the
        # historical-full-profile-leftover pattern (e.g. two decommissioned
        # roots each still holding a stale copy) and must fail.
        write_skill(self.home / ".codex" / "skills", "old-domain-skill", body="same")
        write_skill(self.home / ".cursor" / "skills", "old-domain-skill", body="same")
        entry = {
            "roots": [
                {"path": ".codex/skills", "write_root": None},
                {"path": ".cursor/skills", "write_root": None},
            ],
            "dedup": "undocumented by Cursor; verify empirically",
        }
        lines, ok = audit.audit_agent("cursor", entry, self.home)
        self.assertFalse(ok, "\n".join(lines))
        self.assertTrue(any("PROBLEM" in line and "old-domain-skill" in line for line in lines))

    def test_recursive_agent_catches_nested_duplicate_within_one_root(self):
        # The actual escaped-regression mechanism: Codex, OpenCode, and Cursor all
        # scan recursively by default (verified against their own source/docs; see
        # discovery_graph_notes.md). Two sibling "suite" installs inside the SAME
        # root, each with the same nested skill, must be caught -- a one-level
        # scanner (recursive=False) cannot see this at all.
        base = self.home / ".codex" / "skills"
        write_skill(base / "old-pack", "nested-benchmark", body="v1")
        write_skill(base / "old-pack-reinstall", "nested-benchmark", body="v1")
        entry = {
            "recursive": True,
            "roots": [{"path": ".codex/skills", "write_root": None}],
            "dedup": "by-path, not by name: a same-name skill present at two roots (or at two subdirectories within the SAME root) is shown twice, unmerged",
        }
        lines, ok = audit.audit_agent("codex", entry, self.home)
        self.assertFalse(ok, "\n".join(lines))
        self.assertTrue(any("PROBLEM" in line and "nested-benchmark" in line for line in lines))
        self.assertEqual(
            audit.scan_root(self.home, ".codex/skills", recursive=False),
            {},
            "a one-level (non-recursive) scan of this same fixture must find nothing -- "
            "proving the recursive scan is what catches this, not incidental behavior",
        )

    def test_non_recursive_agent_does_not_see_nested_skills(self):
        # Claude Code (recursive=False) genuinely does not scan into subdirectories.
        # A nested SKILL.md two levels down must not appear in its effective catalog.
        write_skill(self.home / ".claude" / "skills" / "container", "nested-thing")
        entry = {
            "recursive": False,
            "roots": [{"path": ".claude/skills", "write_root": "claude"}],
            "dedup": "single-root; no cross-tool overlap",
        }
        lines, ok = audit.audit_agent("claude-code", entry, self.home)
        self.assertTrue(ok)
        self.assertTrue(any("unique skill names visible: 0" in line for line in lines))

    def test_completion_gate_scoped_to_applied_skills_ignores_unrelated_machine_state(self):
        # distribute_skills.py's post-apply gate must fail on a duplicate among the
        # skills it just placed, but must not fail the whole run over unrelated,
        # pre-existing machine content it never touched (e.g. a personal skill pack
        # with its own internal duplicate) -- that's a separate, pre-existing
        # condition, not something this apply caused or should be blocked by.
        write_skill(self.home / ".agents" / "skills", "git-workflow")
        write_skill(self.home / ".codex" / "skills", "git-workflow")  # stale leftover
        write_skill(self.home / ".codex" / "skills", "unrelated-a", body="x")
        write_skill(self.home / ".codex" / "skills", "unrelated-b", body="x")
        graph = {
            "codex": {
                "roots": [
                    {"path": ".agents/skills", "write_root": "agents"},
                    {"path": ".codex/skills", "write_root": None},
                ],
                "dedup": "by-path, not by name",
            }
        }
        lines, ok = audit.audit_names(graph, self.home, retired=set(), only_names={"git-workflow"})
        self.assertFalse(ok, "\n".join(lines))
        self.assertTrue(any("git-workflow" in line for line in lines))
        self.assertFalse(any("unrelated-a" in line for line in lines))

    def test_no_discovery_roots_populated_exits_clean(self):
        source = self.home / "source"
        source.mkdir()
        (source / "skill-profiles.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "profiles": {"core": []},
                    "targets": {"agents": ".agents/skills"},
                    "discovery_graph": {
                        "codex": {
                            "roots": [{"path": ".agents/skills", "write_root": "agents"}],
                            "dedup": "by-path, not by name",
                        }
                    },
                    "retired_skills": [],
                }
            ),
            encoding="utf-8",
        )
        exit_code = audit.main(["--source", str(source), "--home", str(self.home)])
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
