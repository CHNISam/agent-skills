# Agent Harness

This repository is a **skill library** plus a thin **harness spine**: the small set of
reusable workflows, ladders, and routing rules that make an AI coding agent
token-efficient, mechanically verifiable, and safe to let loose on a real codebase.

It is **not** a framework. There is no runtime, no registry, no package manager, no
vector DB. Skills are plain [Agent Skills](https://github.com/agentskills/agentskills)
(`SKILL.md` + optional `references/` / `scripts/`), discovered and loaded on demand.

GitHub (`CHNISam/agent-skills`) is the durable backup. `origin` is Aliyun codeup.

---

## Design rule: cheapest capable option first

Do not reach for infrastructure. For any capability, walk this ladder and stop at the
first rung that works:

```
native agent/tool ability
  → existing MCP server / tool
  → existing Skill in this repo
  → existing repo script or test
  → GitHub-native mechanism (Actions, reusable workflow, CODEOWNERS, branch protection)
  → a tiny adapter
  → custom infrastructure  (last resort, record why the rungs above failed)
```

`discover → select → load → execute`, never `install everything → preload everything`.
Rare-but-useful skills stay in the repo without being globally loaded.

---

## The four layers

### 1. Capability — MCP / Skills

Skills and MCP servers are first-class, but not all loaded at once. Add a business MCP
(GitHub, DB, Slack, cloud) only when a task needs it; keep the baseline to
**Context7** (latest official docs). Do not install a filesystem MCP — the agent's
native file tools are stronger. See `coding-agent-environment` for the infra baseline
(LSP, ripgrep/fd, per-agent config).

**Is it a Skill?** Keep as a Skill when it is a reusable multi-step workflow that needs
judgment and helps across repos. Otherwise: mechanically checkable → CI/script;
reference knowledge → docs; short universal invariant → AGENTS/CLAUDE; obsolete or
duplicated → delete.

### 2. Context — retrieval ladder

Retrieval cost is a first-class concern. Aim for **minimum relevant context, not maximum**.
Skill: **`context-retrieval`**.

```
known file / already-loaded context
  → LSP  (definition, references, usages, symbols, diagnostics)
  → exact text / grep / glob / filename search
  → semantic repo search / IDE index
  → targeted file reads
  → repo docs / Skills
  → MCP / external sources
```

Do **not** build a custom vector DB, embedding service, RAG server, code indexer, or LSP
proxy unless the existing environment demonstrably cannot answer the need.

### 3. Verification — deterministic gate + judgment

Skill **`automated-testing-workflow`** owns the judgment (scope by risk, diagnose
failures, modification authority). Script **`automated-testing-workflow/scripts/verify.*`**
runs the deterministic gate (format → lint → typecheck → test, fail-fast, exact report).

Risk-based scope: small localized change → targeted tests; normal feature → canonical
repo verification; bug fix → reproduce + regression + prove-gone; large/high-risk →
broad; UI/game → automated checks **plus** real visual evidence. Never declare completion
from code inspection alone. Never weaken or delete tests to make a change pass.

### 4. Change isolation & review

- **Branch / worktree:** `git-workflow` (conventions, safety) + `git-branch-experiment-management`
  (`exp/*` contract, accept/reject/continue). Default: task → short-lived `change/*` branch
  → verify → integrate. A dedicated **worktree per writer** only when writers are truly
  concurrent, or for a risky isolated experiment — not for every sequential task.
- **Review:** `requesting-code-review` for a lightweight self-check before an ordinary
  merge. **`large-change-review`** for broad refactors / high-risk boundaries — it adds a
  risk-tiered diff walkthrough (complete diff vs merge-base, control-flow deltas,
  accidental changes, dead code, missing regression coverage) and an *optional*
  independent read-only reviewer only when size/risk justifies the token cost.
- Do **not** default to spawning subagents or reviewers. Primary agent + tests is enough
  for a normal small feature.

---

## Repository initialization

`init-repository-governance` inspects a target repo and configures **only what applies**:
stack & commands, LSP availability, search-exclusion globs, relevant skills, MCP
recommendations, AGENTS/CLAUDE/Cursor adapters, Git/branch strategy, testing + review
workflow wiring, protected/generated paths, Source-of-Truth routing. It does not install
everything. There is exactly one initialization system — extend it, never fork it.

Instruction files stay thin: `AGENTS.md` = cross-agent entry point (commands, invariants,
completion criteria); `CLAUDE.md` = thin Claude adapter; Cursor rules = scoped; detailed
logic lives in Skills / docs / CI, not in always-loaded prose.

---

## Skill tiers

`core` skills form the harness spine and are candidates for every code repo. `on-demand`
are loaded when the situation calls for them. `domain` are engine/vendor/format/region
specific — available, never globally loaded. `deprecated` are removed or superseded.

### core

| Skill | Role |
|---|---|
| `context-retrieval` | cheap→expensive retrieval ladder (layer 2) |
| `automated-testing-workflow` | risk-based verification judgment + `scripts/verify.*` gate (layer 3) |
| `large-change-review` | risk-tiered diff walkthrough for broad / high-risk changes (layer 4) |
| `git-workflow` | branch strategy, Conventional Commits, history safety |
| `git-branch-experiment-management` | `exp/*` contract, worktree-per-writer, accept/reject/continue |
| `init-repository-governance` | inspect a repo, write tailored thin `AGENTS.md`, wire the harness |
| `coding-agent-environment` | personal infra baseline: LSP, ripgrep/fd, Context7, per-agent config |
| `root-cause-and-verification` | orchestrates: clarify → 5-Why / systematic-debugging → verify-before-claim |
| `writing-skills` | author / edit / test skills (maintain the harness itself) |

Atoms used by `root-cause-and-verification`: `ask-questions-if-underspecified`,
`pause-and-clarify-riper5`, `5-whys-root-cause-analysis`, `systematic-debugging`,
`verification-before-completion`.

### on-demand

`brainstorming` · `writing-plans` · `executing-plans` · `subagent-driven-development` ·
`dispatching-parallel-agents` · `using-git-worktrees` · `finishing-a-development-branch` ·
`requesting-code-review` · `receiving-code-review` · `test-driven-development` ·
`ai-native-sop` · `ai-native-product-spec` · `skill-creator`

### domain

Engine / vendor / format / region specific — e.g. `godot-master`, `godot-agent-vision`,
`claude-api`, `mcp-builder`, `openai-docs`, `shadcn-ui`, the `design*` family,
`docx` / `pdf` / `pptx` / `xlsx`, `playwright`, `webapp-testing`, `screenshot`,
`tcb-connect`, `cloudbase-datamodel`, `clash-verge-claude-routing`, and the
Aliyun / Yunxiao / miniprogram / media workflow skills. Kept available; not harness-core.

### deprecated / removed

- `superpowers/` — was a verbatim duplicate bundle of ~14 top-level skills. **Removed.**
  Top-level skill names are canonical; do not re-nest bundles.
- `codex-resume-handoff/`, `claude-code-enable-mcp/` — empty. **Removed.**
- Unity skills (`unity-cli`, `levelplay-unity-integration`, `build-live-game`,
  `implement-in-app-purchases`, `ui-*`, `optimize-*`, `sprite-editor`, `shader-graph-*`,
  …) — being pruned by the maintainer; tracked as an in-progress working-tree change.

---

## Known cleanup (follow-ups, not this pass)

- `research-writing-assistant/` carries its own nested `.git/` (committed as a bare
  gitlink, no `.gitmodules`). De-vendor to plain files or register a proper submodule.
- Publish a reusable GitHub workflow (`workflow_call`) so consumer repos reference one
  verification pipeline instead of hand-writing CI.
- Migrate the first real consumer (`ElseWake` / `LiteTavern-Prototype`) onto this spine.
