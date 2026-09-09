import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "distribute_skills.py"
SPEC = importlib.util.spec_from_file_location("distribute_skills", SCRIPT)
assert SPEC and SPEC.loader
dist = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dist)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.home = self.root / "home"
        self.source.mkdir()
        self.home.mkdir()
        self.write_skill("alpha", "one")
        self.write_skill("beta", "two")
        self.write_manifest({"core": ["alpha"], "all": "*"})

    def tearDown(self):
        self.temp.cleanup()

    def write_skill(self, name, payload):
        folder = self.source / name
        folder.mkdir(exist_ok=True)
        (folder / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test {name}\n---\n\n{payload}\n",
            encoding="utf-8",
        )

    def write_manifest(self, profiles):
        (self.source / "skill-profiles.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "profiles": profiles,
                    "targets": {"codex": ".codex/skills"},
                    "retired_skills": [],
                }
            ),
            encoding="utf-8",
        )

    def run_dist(self, *args):
        return dist.main(
            [
                "--source",
                str(self.source),
                "--home",
                str(self.home),
                "--target",
                "codex",
                *args,
            ]
        )

    def test_dry_run_does_not_write(self):
        self.assertEqual(self.run_dist("--profile", "core"), 0)
        self.assertFalse((self.home / ".codex" / "skills" / "alpha").exists())

    def test_apply_updates_managed_skill_and_preserves_unrelated_content(self):
        target = self.home / ".codex" / "skills"
        unrelated = target / "private-skill"
        unrelated.mkdir(parents=True)
        (unrelated / "note.txt").write_text("keep", encoding="utf-8")

        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 0)
        self.write_skill("alpha", "updated")
        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 0)

        installed = (target / "alpha" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("updated", installed)
        self.assertEqual((unrelated / "note.txt").read_text(encoding="utf-8"), "keep")
        state = json.loads((target / dist.STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(state["managed_skills"], ["alpha"])

    def test_legacy_state_file_keeps_ownership_and_is_migrated(self):
        target = self.home / ".codex" / "skills"
        managed = target / "alpha"
        managed.mkdir(parents=True)
        (managed / "SKILL.md").write_text("stale", encoding="utf-8")
        (target / ".harness-managed.json").write_text(
            json.dumps(
                {"schema_version": 1, "profile": "core", "managed_skills": ["alpha"]}
            ),
            encoding="utf-8",
        )

        # An install recorded under the old state-file name is still ours, so this
        # must refresh it rather than reporting an unmanaged collision.
        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 0)
        self.assertIn("one", (managed / "SKILL.md").read_text(encoding="utf-8"))
        self.assertFalse((target / ".harness-managed.json").exists())
        state = json.loads((target / dist.STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(state["managed_skills"], ["alpha"])

    def test_unmanaged_collision_requires_explicit_adoption(self):
        target = self.home / ".codex" / "skills" / "alpha"
        target.mkdir(parents=True)
        (target / "local.txt").write_text("unmanaged", encoding="utf-8")

        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 2)
        self.assertTrue((target / "local.txt").exists())
        self.assertEqual(
            self.run_dist("--profile", "core", "--apply", "--adopt-existing"), 0
        )
        self.assertFalse((target / "local.txt").exists())

    def test_prune_removes_only_previously_managed_skills(self):
        self.assertEqual(self.run_dist("--profile", "all", "--apply"), 0)
        target = self.home / ".codex" / "skills"
        unrelated = target / "private-skill"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("keep", encoding="utf-8")

        self.assertEqual(
            self.run_dist("--profile", "core", "--apply", "--prune"), 0
        )
        self.assertTrue((target / "alpha").exists())
        self.assertFalse((target / "beta").exists())
        self.assertTrue(unrelated.exists())

    def test_failed_verification_rolls_back_replacements_and_prunes(self):
        self.assertEqual(self.run_dist("--profile", "all", "--apply"), 0)
        target = self.home / ".codex" / "skills"
        before = (target / "alpha" / "SKILL.md").read_text(encoding="utf-8")
        self.write_skill("alpha", "new-but-invalid")

        real_digest = dist.file_digest
        calls = 0

        def mismatch_once(path):
            nonlocal calls
            calls += 1
            value = real_digest(path)
            return "mismatch" if calls == 2 else value

        with mock.patch.object(dist, "file_digest", side_effect=mismatch_once):
            with self.assertRaises(dist.DistributionError):
                dist.apply_target(
                    target,
                    dist.discover_skills(self.source),
                    ["alpha"],
                    ["beta"],
                    self.source,
                    "core",
                )

        self.assertEqual(
            (target / "alpha" / "SKILL.md").read_text(encoding="utf-8"), before
        )
        self.assertTrue((target / "beta").exists())


if __name__ == "__main__":
    unittest.main()
