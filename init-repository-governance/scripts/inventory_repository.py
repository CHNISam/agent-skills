#!/usr/bin/env python3
"""Print a read-only repository inventory for AGENTS.md authoring and gate wiring."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


INTERESTING_FILES = (
    "AGENTS.md",
    "AGENTS.override.md",
    "CLAUDE.md",
    "README.md",
    "CONTRIBUTING.md",
    "justfile",
    "verify.config",
    "package.json",
    "pnpm-workspace.yaml",
    "yarn.lock",
    "pnpm-lock.yaml",
    "package-lock.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "Makefile",
    "Taskfile.yml",
    "build.gradle",
    "pom.xml",
    "project.godot",
    "docker-compose.yml",
    "compose.yml",
    ".cursorignore",
    ".cursorindexingignore",
)

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next", ".venv", "venv"}

# (marker file, language label, extra search-exclusion globs beyond the common set)
STACK_MARKERS = (
    ("package.json", "javascript/typescript", ["node_modules/", "dist/", ".next/", "coverage/", "*.tsbuildinfo"]),
    ("pyproject.toml", "python", [".venv/", "venv/", "__pycache__/", "*.egg-info/", ".pytest_cache/", ".mypy_cache/", ".ruff_cache/", "htmlcov/"]),
    ("requirements.txt", "python", [".venv/", "venv/", "__pycache__/", ".pytest_cache/"]),
    ("Cargo.toml", "rust", ["target/"]),
    ("go.mod", "go", ["bin/", "vendor/"]),
    ("pom.xml", "java", ["target/"]),
    ("build.gradle", "java/kotlin", ["build/", ".gradle/"]),
    ("Gemfile", "ruby", ["vendor/bundle/", ".bundle/"]),
    ("project.godot", "gdscript/godot", [".godot/", ".import/", "*.blend1", "export_presets.cfg"]),
)

COMMON_SEARCH_EXCLUSIONS = [
    "**/node_modules/**", "**/.venv/**", "**/venv/**", "**/vendor/**",
    "**/dist/**", "**/build/**", "**/out/**", "**/.next/**", "**/bin/**", "**/obj/**",
    "**/.cache/**", "**/.pytest_cache/**", "**/.mypy_cache/**", "**/.ruff_cache/**", "**/.gradle/**", "**/.turbo/**",
    "**/coverage/**", "**/htmlcov/**", "**/*.log",
    "**/*.min.js", "**/*.map",
    "**/package-lock.json", "**/pnpm-lock.yaml", "**/yarn.lock", "**/poetry.lock", "**/Cargo.lock",
    "**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.gif", "**/*.pdf", "**/*.zip", "**/*.mp4", "**/*.wav",
]

# npm script name -> verify stage
NPM_STAGE_SCRIPTS = {"format": "format", "lint": "lint", "typecheck": "typecheck", "build": "typecheck", "test": "test"}


def git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def discover(root: Path) -> list[str]:
    found: list[str] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file() and (path.name in INTERESTING_FILES or path.parent.name in {".github", ".gitlab"}):
            found.append(path.relative_to(root).as_posix())
    return sorted(found)


def _marker_dirs(root: Path, marker: str, max_depth: int = 3) -> list[str]:
    """Relative dirs (root-first) containing `marker`, scanning up to max_depth deep."""
    hits: list[str] = []
    if (root / marker).is_file():
        hits.append(".")
    for path in root.rglob(marker):
        rel = path.relative_to(root)
        parts = rel.parts
        if len(parts) > max_depth or any(p in SKIP_DIRS for p in parts):
            continue
        d = rel.parent.as_posix()
        if d not in hits:
            hits.append(d)
    return hits


def detect_stacks(root: Path) -> tuple[list[str], list[str], dict[str, list[str]]]:
    langs: list[str] = []
    extra_excl: list[str] = []
    locations: dict[str, list[str]] = {}
    for marker, lang, excl in STACK_MARKERS:
        dirs = _marker_dirs(root, marker)
        if not dirs:
            continue
        if lang not in langs:
            langs.append(lang)
        extra_excl.extend(excl)
        locations.setdefault(lang, [])
        for d in dirs:
            if d not in locations[lang]:
                locations[lang].append(d)
    return langs, extra_excl, locations


def _prefix(d: str) -> str:
    return "" if d == "." else f"(cd {d} && "


def _suffix(d: str) -> str:
    return "" if d == "." else ")"


def detect_commands(root: Path, locations: dict[str, list[str]]) -> dict[str, str]:
    """Best-effort verification commands. Never invents — only reports what evidence shows.

    Commands for a nested project are wrapped as `(cd <dir> && ...)`.
    """
    cmds: dict[str, str] = {}

    def put(stage: str, cmd: str) -> None:
        cmds.setdefault(stage, cmd)

    for d in locations.get("javascript/typescript", []):
        base = root if d == "." else root / d
        try:
            scripts = json.loads((base / "package.json").read_text(encoding="utf-8")).get("scripts", {})
        except (ValueError, OSError):
            scripts = {}
        pm = "npm"
        if (base / "pnpm-lock.yaml").is_file():
            pm = "pnpm"
        elif (base / "yarn.lock").is_file():
            pm = "yarn"
        run = "npm run" if pm == "npm" else f"{pm} run"
        put("setup", f"{_prefix(d)}{pm} install{_suffix(d)}")
        for name, stage in NPM_STAGE_SCRIPTS.items():
            if name in scripts:
                put(stage, f"{_prefix(d)}{run} {name}{_suffix(d)}")

    if locations.get("python"):
        d = locations["python"][0]
        if shutil.which("ruff"):
            put("format", f"{_prefix(d)}ruff format --check .{_suffix(d)}")
            put("lint", f"{_prefix(d)}ruff check .{_suffix(d)}")
        if shutil.which("pyright"):
            put("typecheck", f"{_prefix(d)}pyright{_suffix(d)}")
        elif shutil.which("mypy"):
            put("typecheck", f"{_prefix(d)}mypy .{_suffix(d)}")
        if shutil.which("pytest"):
            put("test", f"{_prefix(d)}pytest -q{_suffix(d)}")

    for d in locations.get("rust", []):
        put("format", f"{_prefix(d)}cargo fmt --check{_suffix(d)}")
        put("lint", f"{_prefix(d)}cargo clippy -- -D warnings{_suffix(d)}")
        put("typecheck", f"{_prefix(d)}cargo check{_suffix(d)}")
        put("test", f"{_prefix(d)}cargo test{_suffix(d)}")

    for d in locations.get("go", []):
        put("lint", f"{_prefix(d)}go vet ./...{_suffix(d)}")
        put("test", f"{_prefix(d)}go test ./...{_suffix(d)}")

    # Repo-specific runners are authoritative when present — report, do not assume the invocation.
    for runner in ("run-tests.ps1", "run-tests.sh", "Makefile", "Taskfile.yml", "justfile"):
        for hit in _marker_dirs(root, runner):
            cmds["repo_runner"] = runner if hit == "." else f"{hit}/{runner}"
    return cmds


def detect_lsp(langs: list[str]) -> dict[str, str]:
    """Which language servers are reachable on this machine (executable on PATH)."""
    checks = {
        "javascript/typescript": ("typescript-language-server", "vtsls"),
        "python": ("pyright", "pyright-langserver", "pylsp"),
        "rust": ("rust-analyzer",),
        "go": ("gopls",),
        "java/kotlin": ("jdtls",),
    }
    out: dict[str, str] = {}
    for lang in langs:
        if lang == "gdscript/godot":
            out[lang] = "editor-embedded TCP (127.0.0.1:6005); use gdlint for CLI diagnostics"
            continue
        bins = checks.get(lang, ())
        found = next((b for b in bins if shutil.which(b)), None)
        out[lang] = f"{found} (on PATH)" if found else "no language server on PATH; fall back to CLI linter"
    return out


def suggest_skills(langs: list[str], root: Path) -> dict[str, list[str]]:
    core = [
        "context-retrieval",
        "automated-testing-workflow",
        "git-workflow",
        "git-branch-experiment-management",
        "init-repository-governance",
    ]
    if (root / ".git").exists():
        core.append("large-change-review")
    domain: list[str] = []
    if "gdscript/godot" in langs:
        domain += ["godot-master", "godot-agent-vision"]
    if "javascript/typescript" in langs:
        domain += ["shadcn-ui", "frontend-design", "webapp-testing", "playwright"]
    if (root / "pyproject.toml").is_file():
        domain += ["mcp-builder"]
    return {"core": core, "domain": sorted(set(domain))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    langs, extra_excl, locations = detect_stacks(root)
    search_exclusions = COMMON_SEARCH_EXCLUSIONS + [
        f"**/{g}**" if g.endswith("/") else f"**/{g}" for g in extra_excl
    ]

    payload = {
        "root": str(root),
        "git_toplevel": git(root, "rev-parse", "--show-toplevel"),
        "git_branch": git(root, "branch", "--show-current"),
        "git_status": git(root, "status", "--short", "--branch"),
        "git_remotes": git(root, "remote", "-v"),
        "candidate_files": discover(root),
        "top_level_directories": sorted(
            p.name for p in root.iterdir() if p.is_dir() and p.name not in SKIP_DIRS
        ),
        "languages": langs,
        "stack_locations": locations,
        "verification_commands": detect_commands(root, locations),
        "language_servers": detect_lsp(langs),
        "search_exclusions": sorted(set(search_exclusions)),
        "suggested_skills": suggest_skills(langs, root),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
