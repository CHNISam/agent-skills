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
