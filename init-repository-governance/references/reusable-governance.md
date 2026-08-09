# Reusable Repository Governance

Use this catalog selectively. Repository evidence and explicit user instructions take precedence.

## Contents

- Repository scope and ownership
- Git safety and collaboration
- Requirements and clarification
- Implementation and testing
- Security and data integrity
- UI and prototype fidelity
- External references and licenses
- Completion and reporting
- Tool and browser reuse

## Repository scope and ownership

- Confirm the repository root, working directory, Git remote, current branch, and intended change ownership before implementation.
- In a monorepo or related-repository workspace, map each capability to its owning repository, package, service, and files before editing.
- Keep client, server, infrastructure, migration, credential, and deployment concerns within documented boundaries.
- If existing uncommitted changes appear misplaced, preserve them and stop expanding the problem until the migration scope is confirmed.
- Put shared rules at the root and specialized rules next to the code they govern.

## Git safety and collaboration

Always suitable:

- Before any Git mutation or Git-policy decision, completely read and follow the installed `git-workflow` skill. If it is unavailable, stop before mutations rather than reconstructing it from memory.
- Give every concurrent writing agent or session its own Git worktree and branch, even when planned files do not overlap. Read-only agents may share a worktree.
- Record each writer's absolute worktree path, branch, and file/resource ownership before work starts. Integrate only reviewed commits from those isolated branches.
- If another writer occupies the current worktree or unexplained concurrent changes appear, stop writing and preserve the state. Do not format, stage, commit, or deploy overlapping work until ownership is confirmed.
- Inspect current branch, status, tracking relationship, remote, and exact targets before Git mutations.
- Preserve unrelated and uncommitted user changes; work around them.
- Obtain explicit authorization before destructive or history-rewriting operations.
- Verify important Git claims with fresh command output.
- Prefer non-interactive commands and the repository's established remote protocol.

User-preferred defaults when the repository has no contrary convention:

- Use Conventional Commits: `<type>[scope]: <description>`.
- Use controlled GitFlow: `feature/*` branches start from and return to `develop`; `release/*` promotes validated work from `develop` to `main`; `hotfix/*` starts from `main` and returns to both long-lived branches.
- Keep `main` releasable. Do not develop, commit, or push directly on it.
- Prefer HTTPS remotes unless the user or environment requires SSH.

Choose rather than assume:

- A different branch model when repository evidence conflicts with controlled GitFlow.
- Whether pull requests are mandatory for solo work.
- Tag, release-candidate, staging, approval, and production deployment gates.
- Versioning and release artifact policies.

## Requirements and clarification

- Investigate discoverable answers in documentation, source, configuration, tests, and recorded decisions before asking the user.
- Pause dependent implementation when uncertainty would change user-visible behavior, product scope, domain models, data lifecycle, compatibility, migrations, authentication, authorization, privacy, credentials, correctness criteria, or irreversible infrastructure.
- Ask short, decision-oriented questions and state the impact of each choice.
- After clarification, record the goal, scope, constraints, definition of done, and remaining open questions in the task context or appropriate project artifact.
- When granted discretion, choose reversible, low-risk options consistent with the existing architecture.

## Implementation and testing

- Treat tests as executable statements of confirmed behavior, not obstacles to bypass.
- For features, bug fixes, business-rule changes, and risky refactors: confirm behavior, add or update focused tests, implement, run related checks, then broaden verification in proportion to risk.
- Add missing tests and refactor tests without semantic changes when within scope.
- Require confirmation before changing business expectations or acceptance criteria in tests.
- Do not delete, skip, weaken, or loosen assertions merely to make a run pass.
- Diagnose whether a failure is in product code, test code, environment, or changed requirements before editing.
- Verify commands from manifests, task runners, CI, or project docs. Never invent a command.
- Report exactly which tests and checks ran, their results, what did not run, and remaining risk.

For repositories with low coverage, improve incrementally in this order:

1. The current change.
2. Explicit business rules.
3. High-risk logic.
4. Previously observed regressions.

## Security and data integrity

- Never copy secrets, credentials, private configuration, production data, build artifacts, or unrelated code into the repository.
- Treat authentication, authorization, privacy, credential storage, destructive migrations, and production deployment as explicit decision boundaries.
- Inspect exact targets before delete, overwrite, migration, or broad move operations.
- Prefer reversible changes and scoped permissions.
- Keep environment separation and production gates in project-specific documentation; do not invent vendor-specific controls.

## UI and prototype fidelity

Include these rules only when the repository contains UI or supplied prototypes:

- Treat an approved prototype, design file, or screenshot as an implementation baseline unless the user authorizes redesign.
- Inspect source visuals at original resolution and map each page or state to routes/components and acceptance status.
- Preserve the established visual language, information hierarchy, control placement, and key interaction patterns.
- Reconcile conflicts between functional requirements and prototypes before redesigning.
- Validate at matching viewport sizes with screenshots. Compare layout, proportion, color, typography, spacing, borders, shadows, and visible states.
- State material limitations such as unavailable assets, fonts, or platform differences.
- Select the smallest available design or review skill set that matches the task; do not mandate skills absent from the environment.

## External references and licenses

- Prefer public documentation, source, tests, and history over speculation.
- Adapt patterns to the target repository instead of copying blindly.
- Check license compatibility and preserve required attribution before importing code, configuration, or assets.
- Never copy secrets, private configuration, build outputs, or unrelated implementation from reference repositories.
- Resolve conflicting references in favor of target requirements, current architecture, and explicit user direction.

## Completion and reporting

- Re-read the applicable instruction chain before declaring completion.
- Review the final diff and working-tree status without disturbing unrelated changes.
- Run focused verification first, then broader checks when justified and feasible.
- Report modified files, behavior changes, tests/checks run, failures or omissions, and remaining risks.
- Do not claim tests, deployments, pushes, releases, or visual parity that were not directly verified.

## Tool and browser reuse

- Detect installed tools by executable availability and verified application state. Treat configuration, cache, or compatibility directories only as supporting evidence, not proof that an application is installed.
- Before downloading Chrome, Chromium, a browser driver, Playwright browser binaries, or another large runtime, inspect existing browser executables including non-default and portable paths, then check available Codex/IDE browser connectors.
- Prefer the user's existing browser and profile when it can safely perform the task. Never infer permission to install software from a request to test or screenshot a page.
- Obtain explicit authorization immediately before any browser or driver download.
- For localhost testing, confirm the exact URL, port owner, page title, and a distinctive DOM marker before capturing evidence. Development servers may auto-select another port when the requested port is occupied.
