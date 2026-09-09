# Search / index exclusions

Agent search and semantic indexing should see **only relevant source**. Exclude the
categories below. These are *search* exclusions, not `.gitignore` — some tracked files
(lockfiles) still do not belong in semantic search.

`scripts/inventory_repository.py` emits a `search_exclusions` list tailored to the
detected stack; start from that and adjust.

## Categories to exclude

| Category | Examples |
|---|---|
| Dependencies | `node_modules/`, `vendor/`, `.venv/`, `venv/`, `Pods/`, `target/` |
| Caches | `.cache/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.gradle/`, `.turbo/`, `.import/` |
| Build output | `dist/`, `build/`, `out/`, `.next/`, `bin/`, `obj/`, `.godot/` |
| Generated code | protobuf/gRPC stubs, OpenAPI/GraphQL clients, `*.g.dart`, `*_pb2.py`, `*.generated.*` |
| Minified / sourcemaps | `*.min.js`, `*.min.css`, `*.map` |
| Lockfiles (index only) | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `poetry.lock`, `Cargo.lock` |
| Logs / coverage / reports | `*.log`, `coverage/`, `htmlcov/`, `.nyc_output/`, `test-results/` |
| Binaries / large media | `*.png` `*.jpg` `*.gif` `*.pdf` `*.zip` `*.mp4` `*.wav`, model weights, `*.blend1` |

## Where to configure

| Tool | Mechanism |
|---|---|
| Most coding agents / Cursor | `.gitignore` is respected by default. |
| Cursor (extra) | `.cursorignore` (excluded from AI features + indexing), `.cursorindexingignore` (indexing only). |
| VS Code agent / editor | `search.exclude`, `files.watcherExclude` in workspace settings. |
| ripgrep | `.rgignore` / `.ignore`, or a project `.ripgreprc`. |

Keep the exclusion set in version control so every agent and contributor shares it.
