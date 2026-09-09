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

    def write_manifest(self, profiles, discovery_graph=None, targets=None):
        payload = {
            "schema_version": 1,
            "profiles": profiles,
            "targets": targets or {"codex": ".codex/skills"},
            "retired_skills": [],
        }
        if discovery_graph is not None:
            payload["discovery_graph"] = discovery_graph
        (self.source / "skill-profiles.json").write_text(
            json.dumps(payload), encoding="utf-8",
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

    def test_second_dry_run_after_apply_is_fully_converged(self):
        # Apply, then dry-run again with the same profile: nothing should be
        # pending. This is the idempotency guarantee the discovery-aware
        # redesign depends on -- a converged machine must show zero diff.
        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 0)
        target = self.home / ".codex" / "skills"
        before = sorted(p.name for p in target.iterdir())

        self.assertEqual(self.run_dist("--profile", "core"), 0)  # dry-run

        after = sorted(p.name for p in target.iterdir())
        self.assertEqual(before, after, "dry-run after apply must not report or make changes")

    def test_decommission_dry_run_lists_without_removing(self):
        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 0)
        target = self.home / ".codex" / "skills"

        managed = dist.decommission_target(target, apply=False)

        self.assertEqual(managed, ["alpha"])
        self.assertTrue((target / "alpha").exists())
        self.assertTrue((target / dist.STATE_FILE).exists())

    def test_decommission_apply_removes_only_managed_skills_and_state_file(self):
        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 0)
        target = self.home / ".codex" / "skills"
        unrelated = target / "someone-elses-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("keep me", encoding="utf-8")

        managed = dist.decommission_target(target, apply=True)

        self.assertEqual(managed, ["alpha"])
        self.assertFalse((target / "alpha").exists())
        self.assertFalse((target / dist.STATE_FILE).exists())
        self.assertTrue(unrelated.exists())
        self.assertEqual((unrelated / "SKILL.md").read_text(encoding="utf-8"), "keep me")

    def test_decommission_is_idempotent(self):
        self.assertEqual(self.run_dist("--profile", "core", "--apply"), 0)
        target = self.home / ".codex" / "skills"

        first = dist.decommission_target(target, apply=True)
        second = dist.decommission_target(target, apply=True)

        self.assertEqual(first, ["alpha"])
        self.assertEqual(second, [])

    def test_apply_with_clean_discovery_graph_passes_the_catalog_gate(self):
        # A completion gate exists: after SYNC_OK, the effective-catalog audit
        # runs too, and only a clean result returns exit 0.
        self.write_manifest(
            {"core": ["alpha"], "all": "*"},
            discovery_graph={
                "codex": {
                    "roots": [{"path": ".codex/skills", "write_root": "codex"}],
                    "dedup": "single-root",
                }
            },
        )
        exit_code = self.run_dist("--profile", "core", "--apply")
        self.assertEqual(exit_code, 0)

    def test_apply_fails_the_catalog_gate_when_a_stale_unmanaged_copy_exists(self):
        # This is the exact escaped-regression scenario: the copy this run made is
        # perfectly correct (SYNC_OK), but a second, unmanaged root the same agent
        # also scans already holds a stale copy of the same skill -- the completion
        # gate must catch this and fail the run, not just report SYNC_OK.
        stale_root = self.home / ".legacy" / "skills"
        stale_root.mkdir(parents=True)
        (stale_root / "alpha").mkdir()
        (stale_root / "alpha" / "SKILL.md").write_text(
            "---\nname: alpha\ndescription: test alpha\n---\n\none\n", encoding="utf-8",
        )
        self.write_manifest(
            {"core": ["alpha"], "all": "*"},
            discovery_graph={
                "codex": {
                    "roots": [
                        {"path": ".codex/skills", "write_root": "codex"},
                        {"path": ".legacy/skills", "write_root": None},
                    ],
                    "dedup": "by-path, not by name",
                }
            },
        )
        exit_code = self.run_dist("--profile", "core", "--apply")
        self.assertEqual(exit_code, 3)
        # And the files this run placed are still correct -- the gate reports a
        # problem, it does not roll back a successful, correct copy.
        self.assertTrue((self.home / ".codex" / "skills" / "alpha").exists())

    def test_decommission_on_never_managed_directory_is_a_noop(self):
        target = self.home / ".never" / "touched"
        target.mkdir(parents=True)
        (target / "personal-skill").mkdir()

        managed = dist.decommission_target(target, apply=True)

        self.assertEqual(managed, [])
        self.assertTrue((target / "personal-skill").exists())


if __name__ == "__main__":
    unittest.main()
