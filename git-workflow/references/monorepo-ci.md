# Monorepo Patterns & CI

```bash
# Nx — run targets only for projects affected by the diff
npx nx affected --target=test --base=origin/main --head=HEAD

# Turborepo — same idea via package filter + remote cache
npx turbo run build --filter="...[origin/main]"
```

Both `affected`/`--filter` compare against a base ref, so CI **must fetch git history** — a shallow clone breaks them. With `actions/checkout`, set `fetch-depth: 0` (Nx also offers `nrwl/nx-set-shas` to compute the right base on `main`).

**CODEOWNERS** — `.github/CODEOWNERS` gives per-path required reviewers (pair it with a branch protection rule "Require review from Code Owners"). Last matching pattern wins:

```
# .github/CODEOWNERS
*                       @org/maintainers          # fallback owner
/packages/auth/**       @org/auth-team
/packages/api/**        @org/api-team @alice
/.github/**             @org/platform             # protect CI config itself
*.md                    @org/docs
```

> **CI runner versions (as of Jun 2026):** target Node LTS: Node 22 (LTS "Jod") is the safe default; Node 24 entered LTS in Oct 2025. Node 18 is EOL, so drop it from the matrix. Pin the patch via `.nvmrc`/`actions/setup-node` `node-version-file`, and watch GitHub's runner-image changelog (https://github.com/actions/runner-images) since `ubuntu-latest` periodically moves to a newer default Node.

```yaml
# .github/workflows/ci.yml — typical matrix
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [22, 24]
    steps:
      - uses: actions/checkout@v7
        with: { fetch-depth: 0 }      # needed for affected/--filter and release tooling
      - uses: actions/setup-node@v6
        with: { node-version: ${{ matrix.node }}, cache: npm }
      - run: npm ci
      - run: npm test
```
