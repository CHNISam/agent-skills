---
name: install-skills-global
description: Install/copy skills to AI code editors. Use when user asks to install/copy/sync skills to editors, or mentions syncing skills. Before installing, check which editors the user actually has installed - do not assume all editors exist.
---

# Install Skills Global

This skill helps install/copy agent skills to AI code editors on Windows.

## Workflow

1. **Check which editors the user has** - Ask or detect which editors they use:
   - OpenCode: `%APPDATA%/OpenCode/` or `C:/Users/Administrator/.agents/skills/` (source)
   - Codex: `C:/Users/Administrator/.codex/skills/`
   - Claude Code: `C:/Users/Administrator/.claude/skills/`
   - Antigravity: `C:/Users/Administrator/.antigravity/skills/` (may not exist)
   - Gemini CLI: Check `%USERPROFILE%/gemini/skills/` (may not exist)

2. **Confirm with user** - Show them which editors are available and ask which ones to sync to

3. **Copy skills** - Use `cp -r` to copy skill directories:
   ```bash
   cp -r "source-skills/*" "target-skills/"
   ```
   Note: Ignore errors about `.git/objects/pack/` files.

4. **Verify** - List target skills directory to confirm copy succeeded.

## Common Tasks

- **Install to specific editor**: Copy from source to target editor's skills folder
- **Sync all available**: Copy to all detected editors
- **Check status**: List skills in each editor to see what's installed

## Notes

- Source of truth: `C:/Users/Administrator/.agents/skills/`
- Always check first which editors the user actually has
- Some editors may need restart after copying new skills
