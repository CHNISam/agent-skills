import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "coding-agent-environment"
SCRIPT = SKILL / "scripts" / "manage_claude_code_account.ps1"
REFERENCE = SKILL / "references" / "claude-code-multi-account-windows.md"


class ClaudeCodeMultiAccountSkillTests(unittest.TestCase):
    def test_skill_assets_document_the_supported_isolation_boundary(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        self.assertTrue(REFERENCE.is_file(), "the operating guide must exist")

        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("CLAUDE_CONFIG_DIR", skill)
        self.assertIn("https://code.claude.com/docs/en/authentication#log-in-with-multiple-accounts", reference)
        self.assertIn("https://code.claude.com/docs/en/authentication#authentication-precedence", reference)
        self.assertIn("https://code.claude.com/docs/en/env-vars#claude_config_dir", reference)
        self.assertIn("Claude Console", reference)
        for selector in (
            "CLAUDE_CODE_USE_BEDROCK",
            "CLAUDE_CODE_USE_VERTEX",
            "CLAUDE_CODE_USE_FOUNDRY",
            "ANTHROPIC_PROFILE",
            "ANTHROPIC_FEDERATION_RULE_ID",
            "ANTHROPIC_ORGANIZATION_ID",
        ):
            self.assertIn(selector, script)
            self.assertIn(selector, reference)

    def test_account_manager_never_handles_credential_files_or_tokens(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn(".credentials.json", script)
        self.assertIn("GetEnvironmentVariable", script)
        self.assertNotIn("SetEnvironmentVariable", script)
        self.assertNotIn("Copy-Item", script)

        forbidden_names = {".credentials.json", "credentials.json", "auth.json", ".env"}
        skill_files = [path for path in SKILL.rglob("*") if path.is_file()]
        self.assertFalse(
            [path.relative_to(SKILL) for path in skill_files if path.name.lower() in forbidden_names],
            "the reusable skill must never contain an authentication artifact",
        )
        suspicious_files = [
            path.relative_to(SKILL)
            for path in skill_files
            if path.name.lower().startswith(".env.")
            or path.suffix.lower() in {".pem", ".p12", ".pfx", ".key"}
        ]
        self.assertFalse(
            suspicious_files,
            "the reusable skill must never contain environment or private-key artifacts",
        )
        secret_patterns = (
            re.compile(rb"sk-ant-[a-z0-9_-]{8,}", re.IGNORECASE),
            re.compile(rb"ANTHROPIC_API_KEY\s*[:=]\s*[^\s'\"`]+", re.IGNORECASE),
            re.compile(rb"ANTHROPIC_AUTH_TOKEN\s*[:=]\s*[^\s'\"`]+", re.IGNORECASE),
            re.compile(rb"CLAUDE_CODE_OAUTH_TOKEN\s*[:=]\s*[^\s'\"`]+", re.IGNORECASE),
            re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        )
        leaking_files = [
            path.relative_to(SKILL)
            for path in skill_files
            if any(pattern.search(path.read_bytes()) for pattern in secret_patterns)
        ]
        self.assertFalse(
            leaking_files,
            "the reusable skill must not contain credential-shaped content",
        )
        repository_credentials = [
            path.relative_to(ROOT)
            for path in ROOT.rglob("*")
            if ".git" not in path.parts and path.is_file() and path.name.lower() in {".credentials.json", "credentials.json"}
        ]
        self.assertFalse(
            repository_credentials,
            "the repository must never track Claude credential files",
        )

    def test_focused_distribution_profile_selects_only_this_environment_skill(self):
        manifest = json.loads((ROOT / "skill-profiles.json").read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["profiles"].get("claude-code-multi-account"),
            ["coding-agent-environment"],
        )

    @unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "requires Windows PowerShell")
    def test_apply_verify_is_idempotent_and_rollback_preserves_config_state(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            # Model a non-ASCII Windows user profile. The .cmd must contain
            # only a USERPROFILE expansion, so a repeat Apply and cmd.exe see
            # the same actual isolated path across PowerShell encodings.
            unicode_home = root / "caf\u00e9-user"
            config_dir = unicode_home / "isolated-config"
            primary = bin_dir / "claude.cmd"
            primary.write_bytes(
                b"@echo off\r\n"
                b"if /I \"%~1\"==\"--version\" echo fake-claude 1.0\r\n"
                b"if /I \"%~1\"==\"auth\" (\r\n"
                b"  echo {\"loggedIn\":true,\"configDirectory\":\"%CLAUDE_CONFIG_DIR:\\=/%\"}\r\n"
                b"  exit /b 0\r\n"
                b")\r\n"
                b"exit /b 0\r\n",
            )
            environment = dict(os.environ)
            updated_path = str(bin_dir) + os.pathsep + environment.get(
                "Path", environment.get("PATH", "")
            )
            environment["Path"] = updated_path
            environment["PATH"] = updated_path
            environment["USERPROFILE"] = str(unicode_home)
            # Give the fake primary CLI a valid process-scoped primary directory.
            # This also exercises the manager's effective-primary guard without
            # relying on the real user's home directory.
            environment["CLAUDE_CONFIG_DIR"] = str(root / "primary-config")

            def invoke(*arguments, expect=0):
                completed = subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(SCRIPT),
                        *arguments,
                    ],
                    text=True,
                    capture_output=True,
                    env=environment,
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    expect,
                    f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
                )
                return completed

            common = (
                "-Name",
                "claude2",
                "-ConfigDirectory",
                str(config_dir),
                "-LauncherDirectory",
                str(bin_dir),
                "-ClaudeCommand",
                str(primary),
            )
            invoke("-Action", "Apply", *common)
            launcher = bin_dir / "claude2.cmd"
            self.assertTrue(launcher.is_file())
            launcher_bytes = launcher.read_bytes()
            self.assertTrue(all(byte < 128 for byte in launcher_bytes))
            self.assertIn(b"CLAUDE_CONFIG_DIR=%USERPROFILE%\\isolated-config", launcher_bytes)
            first_digest = hashlib.sha256(launcher.read_bytes()).hexdigest()

            invoke("-Action", "Apply", *common)
            self.assertEqual(first_digest, hashlib.sha256(launcher.read_bytes()).hexdigest())
            invoke("-Action", "Verify", *common)

            wrong_mapping = (
                "-Name",
                "claude2",
                "-ConfigDirectory",
                str(root / "different-config"),
                "-LauncherDirectory",
                str(bin_dir),
                "-ClaudeCommand",
                str(primary),
            )
            invoke("-Action", "Rollback", *wrong_mapping, expect=1)
            self.assertTrue(launcher.is_file(), "rollback must reject a different mapping")

            invoke("-Action", "Rollback", *common)
            self.assertFalse(launcher.exists())
            self.assertTrue(config_dir.is_dir(), "rollback must not delete isolated login state")

    @unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "requires Windows PowerShell")
    def test_apply_refuses_to_replace_primary_or_unmanaged_launcher(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            primary = bin_dir / "claude.cmd"
            primary.write_bytes(b"@echo off\r\nexit /b 0\r\n")
            unmanaged = bin_dir / "claude3.cmd"
            unmanaged_bytes = (
                b"@echo off\r\n"
                b":: agent-skills: managed Claude Code account launcher\r\n"
                b"echo private\r\n"
            )
            unmanaged.write_bytes(unmanaged_bytes)

            def invoke(name):
                return subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(SCRIPT),
                        "-Action",
                        "Apply",
                        "-Name",
                        name,
                        "-ConfigDirectory",
                        str(root / name),
                        "-LauncherDirectory",
                        str(bin_dir),
                        "-ClaudeCommand",
                        str(primary),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )

            self.assertNotEqual(invoke("claude").returncode, 0)
            self.assertNotEqual(invoke("claude3").returncode, 0)
            self.assertEqual(unmanaged.read_bytes(), unmanaged_bytes)

            rollback = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(SCRIPT),
                    "-Action",
                    "Rollback",
                    "-Name",
                    "claude3",
                    "-ConfigDirectory",
                    str(root / "claude3"),
                    "-LauncherDirectory",
                    str(bin_dir),
                    "-ClaudeCommand",
                    str(primary),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(rollback.returncode, 0)
            self.assertEqual(unmanaged.read_bytes(), unmanaged_bytes)

    @unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "requires Windows PowerShell")
    def test_apply_refuses_a_directory_already_selected_by_the_primary_process(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            primary = bin_dir / "claude.cmd"
            primary.write_bytes(b"@echo off\r\nexit /b 0\r\n")
            shared_config = root / "already-primary"
            environment = dict(os.environ)
            environment["CLAUDE_CONFIG_DIR"] = str(shared_config)
            updated_path = str(bin_dir) + os.pathsep + environment.get(
                "Path", environment.get("PATH", "")
            )
            environment["Path"] = updated_path
            environment["PATH"] = updated_path

            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(SCRIPT),
                    "-Action",
                    "Apply",
                    "-Name",
                    "claude2",
                    "-ConfigDirectory",
                    str(shared_config),
                    "-LauncherDirectory",
                    str(bin_dir),
                    "-ClaudeCommand",
                    str(primary),
                ],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("isolated configuration directory", completed.stderr.lower())
            self.assertFalse((bin_dir / "claude2.cmd").exists())

    @unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "requires Windows PowerShell")
    def test_apply_validates_the_launcher_directory_before_creating_config_state(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            primary = bin_dir / "claude.cmd"
            primary.write_bytes(b"@echo off\r\nexit /b 0\r\n")
            config_dir = root / "would-be-config"
            missing_launcher_dir = root / "missing-bin"
            environment = dict(os.environ)
            updated_path = str(bin_dir) + os.pathsep + environment.get(
                "Path", environment.get("PATH", "")
            )
            environment["Path"] = updated_path
            environment["PATH"] = updated_path

            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(SCRIPT),
                    "-Action",
                    "Apply",
                    "-Name",
                    "claude2",
                    "-ConfigDirectory",
                    str(config_dir),
                    "-LauncherDirectory",
                    str(missing_launcher_dir),
                    "-ClaudeCommand",
                    str(primary),
                ],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(config_dir.exists())

    @unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "requires Windows PowerShell")
    def test_verify_requires_an_isolated_logged_in_entry_without_auth_overrides(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            primary = bin_dir / "claude.cmd"
            primary.write_bytes(
                b"@echo off\r\n"
                b"if /I \"%~1\"==\"--version\" echo fake-claude 1.0\r\n"
                b"if /I \"%~1\"==\"auth\" echo {\"loggedIn\":false,\"configDirectory\":\"%CLAUDE_CONFIG_DIR:\\=/%\"}\r\n"
                b"exit /b 0\r\n",
            )
            config_dir = root / "isolated-config"
            environment = dict(os.environ)
            environment["Path"] = str(bin_dir) + os.pathsep + environment.get(
                "Path", environment.get("PATH", "")
            )
            common = [
                "-Name",
                "claude2",
                "-ConfigDirectory",
                str(config_dir),
                "-LauncherDirectory",
                str(bin_dir),
                "-ClaudeCommand",
                str(primary),
            ]

            applied = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Action", "Apply", *common],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            not_logged_in = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Action", "Verify", *common],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertNotEqual(not_logged_in.returncode, 0)

            environment["ANTHROPIC_API_KEY"] = "must-not-leak"
            overridden = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Action", "Verify", *common],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertNotEqual(overridden.returncode, 0)
            self.assertNotIn("must-not-leak", overridden.stdout + overridden.stderr)

            environment.pop("ANTHROPIC_API_KEY")
            environment["ANTHROPIC_PROFILE"] = "outside-config"
            profile_overridden = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Action", "Verify", *common],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertNotEqual(profile_overridden.returncode, 0)
            self.assertNotIn("outside-config", profile_overridden.stdout + profile_overridden.stderr)

            environment.pop("ANTHROPIC_PROFILE")
            environment["CLAUDE_CODE_USE_BEDROCK"] = "1"
            cloud_overridden = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Action", "Verify", *common],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertNotEqual(cloud_overridden.returncode, 0)

    @unittest.skipUnless(os.name == "nt" and shutil.which("powershell"), "requires Windows PowerShell")
    def test_verify_also_checks_the_original_claude_entry(self):
        self.assertTrue(SCRIPT.is_file(), "the Windows account manager must exist")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            primary = bin_dir / "claude.cmd"
            primary.write_bytes(
                b"@echo off\r\n"
                b"if /I \"%~1\"==\"--version\" exit /b 0\r\n"
                b"if /I \"%~1\"==\"auth\" (\r\n"
                b"  if \"%CLAUDE_CONFIG_DIR%\"==\"\" (\r\n"
                b"    echo {\"loggedIn\":false,\"configDirectory\":\"C:/primary\"}\r\n"
                b"  ) else (\r\n"
                b"    echo {\"loggedIn\":true,\"configDirectory\":\"%CLAUDE_CONFIG_DIR:\\=/%\"}\r\n"
                b"  )\r\n"
                b"  exit /b 0\r\n"
                b")\r\n"
                b"exit /b 0\r\n",
            )
            config_dir = root / "isolated-config"
            environment = dict(os.environ)
            environment["Path"] = str(bin_dir) + os.pathsep + environment.get(
                "Path", environment.get("PATH", "")
            )
            common = [
                "-Name",
                "claude2",
                "-ConfigDirectory",
                str(config_dir),
                "-LauncherDirectory",
                str(bin_dir),
                "-ClaudeCommand",
                str(primary),
            ]

            applied = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Action", "Apply", *common],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            verification = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Action", "Verify", *common],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertNotEqual(verification.returncode, 0)
            self.assertIn("Original claude entry is not logged in", verification.stderr)


if __name__ == "__main__":
    unittest.main()
