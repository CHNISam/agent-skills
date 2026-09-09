# .gitignore Best Practices

```gitignore
# OS
.DS_Store
Thumbs.db

# Dependencies
node_modules/
vendor/

# Build output
dist/
.next/
*.tsbuildinfo

# Environment (NEVER commit secrets)
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/settings.json
```

Debug why a path is (not) ignored with `git check-ignore -v <file>`. If a file was committed before being ignored, `.gitignore` won't untrack it — run `git rm --cached <file>` once. Generate a baseline for any stack at https://gitignore.io (CLI: `npx gitignore node python`).

**Language-specific add-ons** (append to the common block above):

```gitignore
# --- Node / JS ---
node_modules/
dist/ build/ .next/ .nuxt/ .turbo/ coverage/
*.tsbuildinfo
.pnpm-store/ .yarn/cache/ .yarn/install-state.gz
npm-debug.log* yarn-error.log* .pnpm-debug.log*

# --- Python ---
__pycache__/ *.py[cod]
.venv/ venv/ env/
*.egg-info/ build/ dist/
.pytest_cache/ .mypy_cache/ .ruff_cache/ .tox/
.coverage htmlcov/

# --- Rust ---
/target/
**/*.rs.bk
# Keep Cargo.lock for binaries; ignore it only for libraries.

# --- Go ---
/bin/ /vendor/
*.exe *.test *.out
go.work go.work.sum

# --- Java / JVM ---
target/ build/ .gradle/
*.class *.jar *.war
.mvn/ !.mvn/wrapper/maven-wrapper.jar

# --- Secrets / local (NEVER commit) ---
.env .env.* !.env.example
*.pem *.key id_rsa* .npmrc
```

> For agent **search/index** exclusions (as opposed to Git tracking), see
> `init-repository-governance/assets/search-exclusions.md` — the two lists overlap but are
> not identical (e.g. you track `package-lock.json` but never want it in semantic search).
