---
name: install-skills-global
description: Install skills to multiple AI code editors (Codex, OpenCode, Claude Code, Antigravity). Use when user asks to install/copy skills to global editors, or wants to sync skills across editors, or mentions "codex", "opencode", "claude", "antigravity" plus "skills".
---

# Install Skills Global

This skill helps install/copy agent skills to multiple AI code editors on Windows.

## Known Editor Skill Paths

| Editor | Path |
|--------|------|
| OpenCode | `C:/Users/Administrator/.agents/skills/` (source) |
| Codex | `C:/Users/Administrator/.codex/skills/` |
| Claude Code | `C:/Users/Administrator/.claude/skills/` |
| Antigravity | `C:/Users/Administrator/.antigravity/skills/` |

## Workflow

1. **Identify source skills** - Determine which skills to copy (usually from `C:/Users/Administrator/.agents/skills/`)

2. **Discover target editor** - Find where the target editor stores skills:
   - Check `%USERPROFILE%/.codex/skills/`
   - Check `%USERPROFILE%/.claude/skills/`
   - Check `%USERPROFILE%/.antigravity/skills/`
   - Check `%APPDATA%/OpenCode/skills/`
   - Check `%APPDATA%/Antigravity/skills/`

3. **Copy skills** - Use `cp -r` to copy skill directories:
   ```bash
   cp -r "source-skills/*" "target-skills/"
   ```
   Note: Some editors may have permission issues with .git directories - ignore errors about `.git/objects/pack/` files.

4. **Verify** - List target skills directory to confirm copy succeeded.

## Common Tasks

- **Install to Codex**: Copy from `.agents/skills/` to `.codex/skills/`
- **Install to Claude Code**: Copy from `.agents/skills/` to `.claude/skills/`
- **Install to Antigravity**: Copy from `.agents/skills/` to `.antigravity/skills/`
- **Sync all**: Copy to multiple editors at once
- **Check status**: List skills in each editor to see what's installed

## Notes

- The source of truth for skills is typically `C:/Users/Administrator/.agents/skills/`
- Some editors may already have skills installed - copy will add new ones without overwriting existing
- Windows paths use forward slashes or escaped backslashes
- After copying, target editor may need restart to recognize new skills
