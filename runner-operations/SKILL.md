---
name: runner-operations
description: "Safely inspect and operate a Windows self-hosted GitHub Actions runner when a project identifies the service, runner, labels, and authorization boundaries. Experimental: do not treat it as a stable automation contract."
---

# Windows self-hosted runner operations

> **Status: Experimental / unstable.** This is safe operating guidance, not a guarantee
> that runner automation or service integration is reliable across hosts. Resolve live
> project configuration for every operation and stop when its state cannot be confirmed.

Use this skill to inspect, temporarily pause, or resume a Windows self-hosted GitHub
Actions runner. It is intentionally generic: the repository, runner name or ID, Windows
service name, labels, baseline command, and ownership rules belong to the project that
uses the runner and must never be guessed or copied from another machine.

## Establish the operating context

Before a project-specific operation:

1. Read the project's agent guidance and runner documentation.
2. Resolve the runner's current identity, online/busy state, and labels through the
   repository's GitHub Actions runners API.
3. Resolve the exact matching Windows service and its startup type locally.
4. Inspect queued and assigned workflow jobs, plus the project's documented baseline
   command where one exists.

Never print or read runner registration credentials, service environment secrets, or
workflow secrets. Do not assume that a local service name or an installed runner belongs
to the requested repository.

## Read-only checks first

Report the GitHub runner state, the matching Windows service state and startup type, its
labels, and any queued or assigned work. If the runner is busy or a job is assigned, do
not interrupt it. Wait for completion or report that the requested action is blocked.

Treat a project's labels as workflow-routing controls. A label can route CI to a personal
machine, so inspect the workflow's selector and the project's baseline before any label
change.

## Mutating operations require explicit authorization

Only pause, resume, change startup type, or add/remove labels after the user explicitly
authorizes that specific effect. If Windows elevation is required, let the owner handle
the native UAC prompt; never automate an owner's confirmation input.

For a temporary pause:

1. Verify that the exact runner is idle.
2. Stop only the resolved Windows service.
3. Verify both the service stopped and the GitHub runner became offline.
4. If the pause must survive restart, record the prior startup type before changing it.

For a resume:

1. Inspect the current startup type.
2. Restore the recorded prior startup type when known. If it is unknown, do not select an
   automatic startup policy without the user's direction.
3. Start the exact resolved service and verify that GitHub reports it online.
4. Do not re-add routing labels unless that was separately authorized.

Do not unregister, uninstall, or replace a runner for a pause. Do not modify workflow
files just to make a runner eligible.

## Report uncertainty explicitly

Every completion report must state the service state, GitHub state, labels changed, work
still running or queued, and any fact that could not be verified. Because this skill is
experimental, report unresolved host-specific behavior instead of treating a successful
command as evidence that the runner is safely configured for future automation.
