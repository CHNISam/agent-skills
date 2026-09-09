# Tag & Release Strategy

```bash
# Manual: annotated, signed tag (lightweight tags lack author/date/message)
git tag -s v2.4.0 -m "Release 2.4.0"   # use -a instead of -s if no GPG/SSH key
git push origin v2.4.0
```

Automate instead of tagging by hand. Two mainstream choices:

| Tool | Model | Best for |
|---|---|---|
| **semantic-release** | Analyzes Conventional Commits on push → bumps, tags, publishes npm, writes changelog, creates GH release — all in CI | Libraries / npm packages, fully hands-off releasing |
| **release-please** (Google) | Opens/maintains a "release PR" that accrues changelog + version bump; you merge it to cut the release | Apps & monorepos, teams that want a human gate before publishing |

> **Runtime (as of Jul 2026):** semantic-release v25 (current) requires Node ^22.14.0 or >= 24.10.0; Node 18 and Node 20 are both end-of-life (Apr 2025 and Apr 2026). It must run against the **full git history**: set `fetch-depth: 0` in the checkout. Pin exact major versions and verify current support at https://github.com/semantic-release/semantic-release/releases and https://github.com/googleapis/release-please.

**semantic-release config** — save as `.releaserc.json`:

```json
{
  "branches": ["main", { "name": "next", "prerelease": true }],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { "changelogFile": "CHANGELOG.md" }],
    "@semantic-release/npm",
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
    }],
    "@semantic-release/github"
  ]
}
```

**release-please config** (GitHub Action) — `.github/workflows/release-please.yml`:

```yaml
name: release-please
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v5
        with:
          release-type: node   # or: simple, python, rust, ...
```
