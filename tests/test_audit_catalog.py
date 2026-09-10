import importlib.util
import json
import shutil
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
        self.assertTrue(any("no duplicate identities" in line for line in lines))

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
            audit.scan_root(self.home / ".codex" / "skills", recursive=False),
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
        self.assertTrue(any("unique skill identities visible: 0" in line for line in lines))

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
        lines, ok = audit.managed_gate(graph, self.home, retired=set(), applied_names={"git-workflow"})
        self.assertFalse(ok, "\n".join(lines))
        self.assertTrue(any("git-workflow" in line for line in lines))
        self.assertFalse(any("unrelated-a" in line for line in lines))

    def test_managed_gate_and_full_audit_are_genuinely_different_checks(self):
        # Item 1's requirement made concrete: the scoped managed gate and the
        # whole-machine full audit must disagree on this exact fixture. A
        # third-party duplicate the gate never looks at (git-workflow is the
        # only applied name) must not make the gate fail, but it MUST make the
        # full audit non-clean -- they are not the same check wearing two names.
        write_skill(self.home / ".agents" / "skills", "git-workflow")
        write_skill(self.home / ".claude" / "skills", "git-workflow")
        write_skill(self.home / ".codex" / "skills", "some-third-party-pack", body="x")
        write_skill(self.home / ".cursor" / "skills", "some-third-party-pack", body="x")
        graph = {
            "codex": {
                "roots": [
                    {"path": ".agents/skills", "write_root": "agents"},
                    {"path": ".codex/skills", "write_root": None},
                    {"path": ".cursor/skills", "write_root": None},
                ],
                "dedup": "by-path, not by name",
            }
        }
        gate_lines, gate_ok = audit.managed_gate(graph, self.home, retired=set(), applied_names={"git-workflow"})
        self.assertTrue(gate_ok, "\n".join(gate_lines))

        manifest = {"retired_skills": []}
        source = self.home / "empty-source"
        source.mkdir()
        full_lines, full_status = audit.full_audit(graph, self.home, manifest, source)
        self.assertEqual(full_status, "REVIEW_REQUIRED", "\n".join(full_lines))

    def test_review_required_can_never_be_reported_as_clean(self):
        # The regression this test pins down: a full-catalog audit with even one
        # unresolved duplicate -- including a third-party one this tool correctly
        # refuses to delete -- must never report CLEAN and must never exit 0.
        # REVIEW_REQUIRED is its own terminal state, distinct from both CLEAN and
        # PROBLEM, with its own exit code, so nothing downstream can quietly treat
        # "not PROBLEM" as "done". If a future change makes this fixture return
        # CLEAN or exit 0, the Done Definition has been narrowed and this must fail.
        write_skill(self.home / ".codex" / "skills", "unknown-third-party-pack", body="x")
        write_skill(self.home / ".cursor" / "skills", "unknown-third-party-pack", body="x")
        source = self.home / "source"
        source.mkdir()
        (source / "skill-profiles.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "profiles": {"core": []},
                    "targets": {},
                    "discovery_graph": {
                        "cursor": {
                            "recursive": True,
                            "roots": [
                                {"path": ".codex/skills", "write_root": None},
                                {"path": ".cursor/skills", "write_root": None},
                            ],
                            "dedup": "undocumented by Cursor; verify empirically",
                        }
                    },
                    "retired_skills": [],
                }
            ),
            encoding="utf-8",
        )
        exit_code = audit.main(["--source", str(source), "--home", str(self.home)])
        self.assertNotEqual(exit_code, 0, "REVIEW_REQUIRED must never exit 0")
        self.assertEqual(exit_code, 2, "REVIEW_REQUIRED has its own exit code, distinct from PROBLEM's 1")

        # Same fixture, direct call: the status string itself must say
        # REVIEW_REQUIRED, never CLEAN, and the duplicate must not have been deleted.
        lines, status = audit.full_audit(
            json.loads((source / "skill-profiles.json").read_text())["discovery_graph"],
            self.home,
            {"retired_skills": []},
            source,
        )
        self.assertEqual(status, "REVIEW_REQUIRED")
        self.assertNotEqual(status, "CLEAN")
        self.assertTrue((self.home / ".codex" / "skills" / "unknown-third-party-pack").exists())
        self.assertTrue((self.home / ".cursor" / "skills" / "unknown-third-party-pack").exists())
        self.assertTrue(any("REVIEW_REQUIRED" in line and "unknown-third-party-pack" in line for line in lines))

    def test_retired_name_nested_in_a_third_party_plugin_is_not_a_finding(self):
        # Real bug found on a real machine: some of this repo's own now-retired
        # skills were themselves verbatim copies of an upstream source (see NOTICE),
        # so a raw, unmodified install of that upstream plugin can be byte-identical
        # to what this repo once shipped and retired -- without being this repo's
        # leftover at all. This repo's own distributor never writes deeper than
        # `<root>/<name>/SKILL.md`; a retired name found nested inside a container
        # (`<root>/superpowers/<name>/SKILL.md`) was not placed by this repo's
        # tooling, so it is a name collision with somebody else's skill and nothing
        # about it is wrong. It gets a NOTE, never a status.
        write_skill(self.home / ".claude" / "skills" / "superpowers", "using-superpowers")
        source = self.home / "source"
        source.mkdir()
        (source / "skill-profiles.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "profiles": {"core": []},
                    "targets": {"claude": ".claude/skills"},
                    "discovery_graph": {
                        "opencode": {
                            "recursive": True,
                            "roots": [{"path": ".claude/skills", "write_root": "claude"}],
                            "dedup": "by name, last-scan-wins",
                        }
                    },
                    "retired_skills": ["using-superpowers"],
                }
            ),
            encoding="utf-8",
        )
        manifest = json.loads((source / "skill-profiles.json").read_text())
        lines, status = audit.full_audit(manifest["discovery_graph"], self.home, manifest, source)
        self.assertEqual(status, "CLEAN", "\n".join(lines))
        self.assertTrue(any(l.strip().startswith("NOTE:") and "using-superpowers" in l for l in lines))
        self.assertFalse(any(l.strip().startswith("PROBLEM") and "using-superpowers" in l for l in lines))
        # And a directly-placed retired copy (this repo's own actual placement shape)
        # in the SAME fixture is still a real PROBLEM, not swept into REVIEW_REQUIRED.
        write_skill(self.home / ".claude" / "skills", "using-superpowers")
        lines2, status2 = audit.full_audit(manifest["discovery_graph"], self.home, manifest, source)
        self.assertEqual(status2, "PROBLEM", "\n".join(lines2))

    def test_non_retired_name_only_visible_via_nesting_is_review_required(self):
        # The other half of the real bug: not just retired names, but ANY currently-
        # canonical name (e.g. "brainstorming") that this repo does place directly at
        # one root can ALSO coincidentally match a nested third-party plugin copy
        # elsewhere. classify_duplicate must not call that a mechanically-fixable
        # PROBLEM just because the name is recognized and the content matches --
        # the nested copy is still not this repo's placement to remove.
        write_skill(self.home / ".claude" / "skills", "brainstorming")
        write_skill(self.home / ".cursor" / "skills" / "superpowers", "brainstorming")
        entry = {
            "recursive": True,
            "roots": [
                {"path": ".claude/skills", "write_root": "claude"},
                {"path": ".cursor/skills", "write_root": None},
            ],
            "dedup": "undocumented by Cursor; verify empirically",
        }
        by_skill = audit.collect_contributions(entry, self.home)
        status, reason = audit.classify_duplicate(
            "brainstorming", by_skill["brainstorming"], known_names={"brainstorming"}, retired=set()
        )
        self.assertEqual(status, "REVIEW_REQUIRED", reason)

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


def write_plugin(root: Path, plugin: str, skill: str, body: str = "content") -> Path:
    """A plugin-shaped install: `<root>/<plugin>/skills/<skill>/SKILL.md` next to a
    plugin manifest. The runtime keys these as `<plugin>:<skill>`."""
    plugin_root = root / plugin
    (plugin_root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": plugin, "version": "1.0.0"}), encoding="utf-8"
    )
    write_skill(plugin_root / "skills", skill, body=body)
    return plugin_root / "skills" / skill


CODEX_ENTRY = {
    "recursive": True,
    "roots": [
        {"path": ".agents/skills", "write_root": "agents"},
        {"path": ".codex/skills", "write_root": None},
    ],
    "dedup": "by-path, not by name: a same-name skill present at two roots is shown twice, unmerged",
}


class LogicalIdentityTests(unittest.TestCase):
    """The invariant is about the identity an agent's catalog actually keys on. That is
    NOT the bare frontmatter name whenever a skill ships inside a plugin -- verified
    against the live Codex runtime, see discovery_graph_notes.md."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_plugin_owned_skill_is_namespaced_by_its_plugin(self):
        skill_dir = write_plugin(self.home / ".agents" / "skills", "superpowers", "brainstorming")
        self.assertEqual(
            audit.logical_id(self.home / ".agents" / "skills", skill_dir, "brainstorming"),
            "superpowers:brainstorming",
        )

    def test_standalone_skill_keeps_its_bare_name(self):
        write_skill(self.home / ".agents" / "skills", "brainstorming")
        skill_dir = self.home / ".agents" / "skills" / "brainstorming"
        self.assertEqual(
            audit.logical_id(self.home / ".agents" / "skills", skill_dir, "brainstorming"),
            "brainstorming",
        )

    def test_plugin_copy_and_standalone_copy_are_not_duplicates(self):
        # The false positive a bare-name comparison produces: a plugin's own
        # `brainstorming` and a standalone `brainstorming` are two distinct catalog
        # entries (`superpowers:brainstorming` and `brainstorming`), not one skill twice.
        # Collapsing them would remove a skill the user legitimately has.
        root = self.home / ".agents" / "skills"
        write_skill(root, "brainstorming", body="standalone")
        write_plugin(root, "superpowers", "brainstorming", body="from the pack")
        lines, ok = audit.audit_agent("codex", CODEX_ENTRY, self.home)
        self.assertTrue(ok, "\n".join(lines))
        self.assertTrue(any("no duplicate identities" in line for line in lines))

    def test_same_plugin_installed_under_two_roots_is_a_duplicate(self):
        # The false negative: both copies resolve to the same namespaced identity, so
        # this really is one logical skill reachable twice.
        write_plugin(self.home / ".agents" / "skills", "bencium", "ux-designer")
        write_plugin(self.home / ".codex" / "skills", "bencium", "ux-designer")
        lines, ok = audit.audit_agent("codex", CODEX_ENTRY, self.home)
        self.assertFalse(ok, "\n".join(lines))
        self.assertTrue(any("bencium:ux-designer" in line for line in lines))

    def test_namespace_is_found_through_a_symlinked_plugin_skills_directory(self):
        # How superpowers is really installed: only the plugin's inner `skills/`
        # directory is linked into the discovery root, so the manifest sits above the
        # link *target* and an unresolved walk would never see it.
        elsewhere = self.home / "packs"
        write_plugin(elsewhere, "superpowers", "brainstorming")
        root = self.home / ".agents" / "skills"
        root.mkdir(parents=True, exist_ok=True)
        try:
            (root / "superpowers").symlink_to(
                elsewhere / "superpowers" / "skills", target_is_directory=True
            )
        except (OSError, NotImplementedError) as exc:  # unprivileged Windows, etc.
            self.skipTest(f"symlinks unavailable here: {exc}")
        found = audit.scan_root(root, recursive=True)
        self.assertIn("superpowers:brainstorming", found)


class DuplicateInvariantTests(unittest.TestCase):
    """The reported failure and its exact recovery: one bundle installed twice under
    two container names inside a single recursive root."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.source = self.home / "source"
        self.source.mkdir()
        self.manifest = {"retired_skills": [], "duplicate_exceptions": []}
        self.graph = {"codex": CODEX_ENTRY}

    def tearDown(self):
        self.temp.cleanup()

    def _audit(self):
        return audit.full_audit(
            self.graph, self.home, self.manifest, self.source, project=self.home / "nowhere"
        )

    def test_one_bundle_installed_twice_fails_with_evidence(self):
        base = self.home / ".codex" / "skills"
        write_skill(base / "blender-agent-studio", "blender-agent-benchmark", body="same")
        write_skill(base / "blender-agent-studio-suite", "blender-agent-benchmark", body="same")
        lines, status = self._audit()
        self.assertNotEqual(status, "CLEAN")
        finding = next(line for line in lines if "blender-agent-benchmark" in line and "paths=" in line)
        # The evidence the harness must carry: identity, agent, every path, and why.
        self.assertIn("agent=codex", finding)
        self.assertIn("identity='blender-agent-benchmark'", finding)
        self.assertIn("blender-agent-studio-suite", finding)
        self.assertIn("why=", finding)

    def test_removing_the_duplicate_makes_it_clean_again(self):
        base = self.home / ".codex" / "skills"
        write_skill(base / "blender-agent-studio", "blender-agent-benchmark", body="same")
        write_skill(base / "blender-agent-studio-suite", "blender-agent-benchmark", body="same")
        self.assertNotEqual(self._audit()[1], "CLEAN")
        shutil.rmtree(base / "blender-agent-studio")
        self.assertEqual(self._audit()[1], "CLEAN")

    def test_project_scoped_root_can_collide_with_a_user_root(self):
        # A repository that vendors a skill also installed globally shows it twice.
        # Modelling only home-relative roots would miss this entirely.
        project = self.home / "workspace"
        graph = {
            "codex": {
                "recursive": True,
                "roots": [
                    {"path": ".agents/skills", "write_root": "agents"},
                    {"path": ".agents/skills", "base": "project", "write_root": None},
                ],
                "dedup": "by-path, not by name",
            }
        }
        write_skill(self.home / ".agents" / "skills", "context-retrieval")
        write_skill(project / ".agents" / "skills", "context-retrieval")
        _lines, status = audit.full_audit(graph, self.home, self.manifest, self.source, project=project)
        self.assertNotEqual(status, "CLEAN")

    def test_install_gated_roots_are_declared_but_never_walked(self):
        entry = {
            "recursive": True,
            "roots": [{"path": ".codex/plugins/cache", "write_root": None, "install_gated": True}],
            "dedup": "by-path, not by name",
        }
        write_plugin(self.home / ".codex" / "plugins" / "cache", "visualize", "visualize")
        self.assertEqual(audit.collect_contributions(entry, self.home, self.home), {})


class DuplicateExceptionTests(unittest.TestCase):
    """An exception is the ONLY sanctioned way a duplicate may persist, and it has to be
    exact: agent, identity, and the full set of contributing paths."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.source = self.home / "source"
        self.source.mkdir()
        self.graph = {"codex": CODEX_ENTRY}
        write_skill(self.home / ".agents" / "skills", "openai-docs", body="ours")
        write_skill(self.home / ".codex" / "skills", "openai-docs", body="theirs")

    def tearDown(self):
        self.temp.cleanup()

    def _audit(self, exceptions):
        manifest = {"retired_skills": [], "duplicate_exceptions": exceptions}
        return audit.full_audit(self.graph, self.home, manifest, self.source, project=self.home / "nowhere")

    def exception(self, paths):
        return {
            "agent": "codex",
            "logical_id": "openai-docs",
            "paths": paths,
            "reason": "two genuinely different skills that happen to share a name",
            "reviewed": "2026-09-10",
        }

    def test_without_an_exception_the_duplicate_fails(self):
        _lines, status = self._audit([])
        self.assertNotEqual(status, "CLEAN")

    def test_an_exact_exception_acknowledges_it(self):
        lines, status = self._audit(
            [self.exception([".agents/skills/openai-docs", ".codex/skills/openai-docs"])]
        )
        self.assertEqual(status, "CLEAN", "\n".join(lines))
        self.assertTrue(any("ACKNOWLEDGED" in line for line in lines))

    def test_an_exception_listing_the_wrong_paths_does_not_apply(self):
        # It must not be possible to write a loose exception that silently covers a
        # duplicate at some other path nobody reviewed.
        lines, status = self._audit(
            [self.exception([".agents/skills/openai-docs", ".cursor/skills/openai-docs"])]
        )
        self.assertNotEqual(status, "CLEAN", "\n".join(lines))

    def test_a_stale_exception_is_itself_a_problem(self):
        # Waiver hygiene: once the duplicate is gone the exception must go too, or it
        # sits there pre-approving a future duplicate nobody looked at.
        shutil.rmtree(self.home / ".codex" / "skills" / "openai-docs")
        lines, status = self._audit(
            [self.exception([".agents/skills/openai-docs", ".codex/skills/openai-docs"])]
        )
        self.assertEqual(status, "PROBLEM", "\n".join(lines))
        self.assertTrue(any("stale exception" in line for line in lines))


class RuntimeCatalogParsingTests(unittest.TestCase):
    """The runtime cross-check is what keeps the static model honest, so its parsing of
    an agent's own rendered catalog is itself pinned down."""

    BLOCK = (
        "<skills_instructions>\n"
        "### Skill roots\n"
        "- `r0` = `/home/u/.codex/skills`\n"
        "- `r1` = `/home/u/.agents/skills`\n"
        "### Available skills\n"
        "- git-workflow: Branching, commits (file: r1/git-workflow/SKILL.md)\n"
        "- superpowers:brainstorming: Ideas into designs (file: r1/superpowers/brainstorming/SKILL.md)\n"
        "</skills_instructions>\n"
    )

    def test_parses_ids_and_absolute_paths(self):
        parsed = audit.parse_runtime_catalog(self.BLOCK)
        self.assertIn(("git-workflow", str(Path("/home/u/.agents/skills/git-workflow"))), parsed)

    def test_keeps_the_namespace_in_a_namespaced_id(self):
        ids = {identity for identity, _ in audit.parse_runtime_catalog(self.BLOCK)}
        self.assertIn("superpowers:brainstorming", ids)

    def test_extracts_the_block_from_a_json_prompt_dump(self):
        payload = json.dumps([{"role": "developer", "content": [{"type": "input_text", "text": self.BLOCK}]}])
        self.assertEqual(audit.extract_skills_block(payload), self.BLOCK)


BY_PATH_ENTRY = {
    "recursive": True,
    "dedup_kind": "by-path",
    "roots": [
        {"path": ".agents/skills", "write_root": "agents"},
        {"path": ".codex/skills", "write_root": None},
    ],
    "dedup": "by-path, not by name: shown twice, unmerged",
}

BY_NAME_ENTRY = {
    "recursive": True,
    "dedup_kind": "by-name",
    "roots": [
        {"path": ".claude/skills", "write_root": "claude"},
        {"path": ".agents/skills", "write_root": "agents"},
        {"path": ".cursor/skills", "write_root": None},
    ],
    "dedup": "by name, last-scan-wins, logs a warning on collision",
}


class DedupSemanticsTests(unittest.TestCase):
    """"Two files exist" and "the user sees the skill twice" are different claims. Only
    the second is a defect, and which one a given set of paths amounts to is decided by
    the agent's own dedup rule, not by the filesystem."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.source = self.home / "source"
        self.source.mkdir()
        self.manifest = {"retired_skills": [], "duplicate_exceptions": []}

    def tearDown(self):
        self.temp.cleanup()

    def _audit(self, graph):
        return audit.full_audit(
            graph, self.home, self.manifest, self.source, project=self.home / "nowhere"
        )

    def test_by_name_agent_reading_two_populated_shared_roots_is_clean(self):
        # The false positive this test exists for: an agent that merges by identity
        # reads several roots this repo deliberately populates. Cross-agent reuse is
        # the intended design, and the user sees one entry.
        write_skill(self.home / ".claude" / "skills", "git-workflow", body="X")
        write_skill(self.home / ".agents" / "skills", "git-workflow", body="X")
        lines, status = self._audit({"opencode": BY_NAME_ENTRY})
        self.assertEqual(status, "CLEAN", "\n".join(lines))
        self.assertTrue(any("DEDUPED" in line and "git-workflow" in line for line in lines))

    def test_by_name_agent_is_clean_even_when_the_copies_differ(self):
        # Divergent content under last-scan-wins is a question of WHICH copy is live,
        # not of how many entries exist. The catalog still shows exactly one.
        write_skill(self.home / ".claude" / "skills", "git-workflow", body="old")
        write_skill(self.home / ".agents" / "skills", "git-workflow", body="new")
        write_skill(self.home / ".cursor" / "skills", "git-workflow", body="third")
        lines, status = self._audit({"opencode": BY_NAME_ENTRY})
        self.assertEqual(status, "CLEAN", "\n".join(lines))

    def test_the_same_fixture_is_a_real_duplicate_on_a_by_path_agent(self):
        # Detection is not weakened, it is made specific: identical paths, opposite
        # verdict, decided purely by what the agent does with them.
        write_skill(self.home / ".agents" / "skills", "git-workflow", body="X")
        write_skill(self.home / ".codex" / "skills", "git-workflow", body="X")
        _lines, by_path = self._audit({"codex": BY_PATH_ENTRY})
        self.assertNotEqual(by_path, "CLEAN")
        _lines, by_name = self._audit({"opencode": dict(BY_PATH_ENTRY, dedup_kind="by-name")})
        self.assertEqual(by_name, "CLEAN")

    def test_dedup_kind_defaults_to_the_strict_reading(self):
        # An agent whose rule nobody has established must be treated as the kind that
        # can actually show duplicates, so an unverified claim never silences one.
        self.assertEqual(audit.dedup_kind({}), "by-path")


class AliasCollapseTests(unittest.TestCase):
    """Shared roots are routinely wired up by linking one agent's directory into
    another's. Reading one directory through two names is one skill, not two."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.source = self.home / "source"
        self.source.mkdir()
        self.manifest = {"retired_skills": [], "duplicate_exceptions": []}

    def tearDown(self):
        self.temp.cleanup()

    def _link(self, link: Path, target: Path):
        link.parent.mkdir(parents=True, exist_ok=True)
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:  # unprivileged Windows, etc.
            self.skipTest(f"symlinks unavailable here: {exc}")

    def test_one_directory_reached_through_two_roots_is_one_contribution(self):
        write_skill(self.home / ".codex" / "skills", "blender-scene-design")
        self._link(self.home / ".cursor" / "skills" / "blender-scene-design",
                   self.home / ".codex" / "skills" / "blender-scene-design")
        entry = {
            "recursive": True,
            "dedup_kind": "by-path",
            "roots": [
                {"path": ".codex/skills", "write_root": None},
                {"path": ".cursor/skills", "write_root": None},
            ],
            "dedup": "by-path, not by name",
        }
        contributions = audit.collect_contributions(entry, self.home, self.home)["blender-scene-design"]
        self.assertEqual(len(contributions), 1)
        # The alias is kept as evidence, so a reader still sees both routes.
        self.assertEqual(len(contributions[0].aliases), 1)
        self.assertIn("same directory also reached as", contributions[0].describe())

    def test_an_alias_is_clean_on_a_by_path_agent_but_a_real_second_copy_is_not(self):
        # The distinction that matters: a link and a copy look alike on a path listing
        # and are opposites in the catalog.
        write_skill(self.home / ".codex" / "skills", "blender-scene-design")
        self._link(self.home / ".cursor" / "skills" / "blender-scene-design",
                   self.home / ".codex" / "skills" / "blender-scene-design")
        entry = {
            "recursive": True,
            "dedup_kind": "by-path",
            "roots": [
                {"path": ".codex/skills", "write_root": None},
                {"path": ".cursor/skills", "write_root": None},
            ],
            "dedup": "by-path, not by name",
        }
        _lines, status = audit.full_audit(
            {"cursor": entry}, self.home, self.manifest, self.source, project=self.home / "nowhere"
        )
        self.assertEqual(status, "CLEAN")

        write_skill(self.home / ".codex" / "skills" / "second-pack", "blender-scene-design")
        _lines, status = audit.full_audit(
            {"cursor": entry}, self.home, self.manifest, self.source, project=self.home / "nowhere"
        )
        self.assertNotEqual(status, "CLEAN")
