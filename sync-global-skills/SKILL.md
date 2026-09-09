---
name: sync-global-skills
description: Publish reviewed changes from the canonical agent-skills Git worktree to its configured remotes, then refresh managed local agent installations. Use only when the user explicitly asks to back up, push, publish, or synchronize the shared skill library.
---

# Publish and Synchronize the Skill Library

The Git worktree is authoritative. Never rebuild it by deleting folders and copying back
from `~/.agents/skills` or another generated target.

## Safe sequence

1. Inspect repository root, branch, both remotes, status, and all worktrees. Preserve
   unrelated or uncommitted changes.
2. Author changes on a short-lived branch. If an installed copy contains unique edits,
   compare and import only the intended files into the branch; do not bulk overwrite.
3. Run:

   ```bash
   python scripts/validate_repo.py
   python -m unittest discover -s tests -p "test_*.py" -v
   ```

4. Review the complete diff, commit with a meaningful Conventional Commit, and push the
   branch to the requested remotes. Use a PR for integration unless the user explicitly
   directs a permitted direct update.
5. After the canonical branch is integrated and pulled locally, refresh installed copies:

   ```bash
   python scripts/distribute_skills.py --profile core --target all --apply --prune
   ```

6. Verify remote SHAs and the distributor's `SYNC_OK` result before reporting success.

Do not force-push, rewrite history, silently change remotes, or treat a successful GitHub
push as proof that another remote or the local agent installations were updated.
