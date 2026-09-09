---
name: context-retrieval
description: Cheap-to-expensive ladder for retrieving code and context so the agent loads the minimum relevant context, not the maximum. Use when locating a definition/caller/usage, understanding an unfamiliar area, deciding whether to read a whole file, choosing between grep and semantic search, or when a task is tempting you to read large parts of the repository. Also use when setting up or auditing a repository's search/index exclusions.
---

# Context Retrieval

Retrieval cost — tokens and latency — is a first-class engineering concern. The goal is
**minimum relevant context, not maximum context**. Answering a question by reading the
whole repository is almost always the wrong move.

## The ladder

Start at the top. Stop at the first rung that answers the question. Only descend when the
current rung genuinely cannot.

1. **Known context** — a file path the user gave you, a symbol already in the
   conversation, a doc you already read. Use it directly; do not re-derive.
2. **LSP / language intelligence** — go-to-definition, find-references, find-usages,
   document/workspace symbols, hover types, diagnostics. This is exact, structural, and
   cheap. Prefer it over reading files to answer "where is X defined / who calls X / what
   type is X / what's broken". Requires a language server for the stack (see
   `coding-agent-environment` for setup; some servers like Godot's only expose a TCP port
   and only certain editors can reach them).
3. **Exact text search** — `grep` / ripgrep for strings, `glob` / `fd` for filenames.
   Use for literals, error messages, config keys, unique identifiers, TODO markers.
   Faster and more predictable than semantic search when you know the token.
4. **Semantic / index search** — the editor or coding agent's built-in codebase index
   (VS Code workspace context, Cursor semantic search, etc.). Use when you *don't* know
   the exact token — "where is auth session expiry handled", "the retry logic for uploads".
   It returns candidates; confirm them with rung 2 or 3 before acting.
5. **Targeted file reads** — read the specific ranges the rungs above pointed you at, not
   whole files, and not whole directories. Widen only when a range proves insufficient.
6. **Repo docs / Skills** — `README`, `AGENTS.md`, `docs/`, ADRs, and any domain skill
   for this stack. Reference knowledge that is written down beats re-inferring it.
7. **MCP / external sources** — Context7 for latest library docs, web, other MCP servers.
   Last, because it is the most expensive and least specific to this repo.

## Do not build retrieval infrastructure

Use the mature capabilities that already exist in the editor / coding agent. Do **not**
build a custom vector database, embedding service, RAG server, code indexer, dependency
grapher, or LSP proxy. Tree-sitter and codebase indexing already run inside the tools —
watch them, do not reimplement them. Only consider custom retrieval if the existing
environment *demonstrably* cannot satisfy a concrete, recurring need — and record why.

## Search/index exclusions

Good retrieval depends on a clean search corpus. A repository should exclude from agent
search and semantic indexing (not necessarily from Git):

- dependencies (`node_modules/`, `vendor/`, `.venv/`, `Pods/`, `target/`)
- caches (`.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.gradle/`, `.turbo/`)
- build outputs (`dist/`, `build/`, `.next/`, `out/`, `bin/`, `obj/`)
- generated code (protobuf/gRPC stubs, OpenAPI clients, `*.g.dart`, `*_pb2.py`)
- lockfiles for semantic search (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`)
- logs, coverage, reports (`*.log`, `coverage/`, `htmlcov/`, `.nyc_output/`)
- binaries and large artifacts (`*.png` beyond a threshold, `*.pdf`, `*.zip`, media,
  model weights, `.import/` caches, `*.blend1`)

Configure via `.gitignore` (Cursor and most agents respect it), `.cursorignore` /
`.cursorindexingignore`, or the editor's `search.exclude` / `files.watcherExclude`.
`init-repository-governance` proposes a tailored list per repo — see
`init-repository-governance/assets/search-exclusions.md`.

## Anti-patterns

- Reading a directory tree "to get oriented" before you have a specific question.
- `grep`-ing a concept ("cache") and reading every hit, when LSP find-references on the
  actual symbol would be exact.
- Reading a whole 2000-line file for one function LSP could have jumped to.
- Reaching for web / MCP docs before checking the repo's own `docs/` and skills.
- Re-reading a file already in context to "double-check".

## Upstream references

VS Code agent *workspace context* and *context* documentation; Cursor *semantic search*
and *secure codebase indexing* engineering posts; Anthropic *advanced tool use* and
*writing tools for agents*. Concepts only — no code imported.
