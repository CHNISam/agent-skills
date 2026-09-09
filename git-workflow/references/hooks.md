# Git Hooks (Husky + lint-staged + commitlint)

Husky **v9+** changed the setup: there is no `husky add`/`husky install` anymore. Run `husky init`, then write hook files directly (a hook is just a shell script; no `#!/bin/sh` shebang or `husky.sh` sourcing line is needed in v9+).

```bash
# 1. Install tooling
npm i -D husky lint-staged @commitlint/cli @commitlint/config-conventional

# 2. Scaffold .husky/ and add the "prepare" script to package.json
npx husky init        # creates .husky/pre-commit (with "npm test") + sets "prepare": "husky"

# 3. commitlint config (commitlint.config.mjs — ESM is the current default)
printf "export default { extends: ['@commitlint/config-conventional'] };\n" > commitlint.config.mjs
```

```json
// package.json
{
  "scripts": { "prepare": "husky" },
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

Write the two hook files directly (overwrite the placeholder `npx husky init` left in `pre-commit`):

```bash
# .husky/pre-commit  — lint only staged files
npx lint-staged
```

```bash
# .husky/commit-msg  — validate the message against Conventional Commits
npx --no-install commitlint --edit "$1"
```

> Husky obeys `core.hooksPath`, so it only fires from the repo root after a real `npm install`. To bypass in an emergency: `git commit --no-verify` (or `HUSKY=0 git commit ...`). On CI, hooks should not run — guard `prepare` or set `HUSKY=0` in the workflow env so `npm ci` doesn't try to scaffold hooks.

## Reusable PR template

Save as `.github/PULL_REQUEST_TEMPLATE.md` (GitHub auto-loads it into the PR description; for multiple templates use `.github/PULL_REQUEST_TEMPLATE/<name>.md` and `?template=<name>.md`):

```markdown
## What & why
<!-- One paragraph: the change and the problem it solves. Link the issue. -->
Closes #

## Type of change
- [ ] fix (PATCH)   - [ ] feat (MINOR)   - [ ] breaking (MAJOR)
- [ ] chore / docs / refactor / test / ci (no release)

## How to test
1.
2.

## Checklist
- [ ] PR < ~400 lines (or explained why not)
- [ ] Tests added/updated and passing locally
- [ ] No secrets/PII in diff
- [ ] Breaking changes documented + migration notes
- [ ] DB migrations reversible
- [ ] Docs/changelog updated if user-facing

## Screenshots / logs
<!-- UI changes: before/after. Backend: relevant log or curl output. -->
```
