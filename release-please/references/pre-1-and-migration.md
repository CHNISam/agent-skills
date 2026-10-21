# Pre-1.0 policy, delivery cadence, and history migration

## Release policy is project-owned

SemVer 2.0.0 states `0.y.z` is for initial development and public API stability is not promised. The following is a **deliberate optional policy**, not a SemVer mandate:

- While major = 0, breaking changes → bump minor (`0.2.4 → 0.3.0`).
- While major = 0, compatible features or bug fixes → bump patch (`0.2.4 → 0.2.5`).
- A **single release** containing 10 features bumps the chosen version component once, not ten times. Merges and commits alone do not create ten release versions.
- After 1.0, use normal SemVer: breaking → major, feature → minor, bugfix → patch.

Release Please supports this policy with these manifest options:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "release-type": "simple",
  "bump-minor-pre-major": true,
  "bump-patch-for-minor-pre-major": true,
  "packages": {
    ".": {
      "release-type": "simple"
    }
  }
}
```

These settings are expressly documented by Release Please's [configuration schema](https://github.com/googleapis/release-please/blob/main/schemas/config.json) and [default versioning strategy](https://github.com/googleapis/release-please/blob/main/src/versioning-strategies/default.ts). They modify the `0.x` bump rules; don't assume generic Conventional Commits guidance already implements them. A major new stage without a breaking change requires an explicit, reviewed version decision rather than an inferred `feat:` bump.

## Keep development separate from releasing

1. Accumulate Conventional Commits from PRs on the project's chosen integration branch.
2. Run Release Please on the **authorized release baseline** (which may differ from the integration branch), opening/updating one Release PR for all changes since the last released version.
3. Review the proposed next version and human-readable changelog, validate the exact source and build, and obtain the project's release approval.
4. Merge the approved Release PR to create the version tag and GitHub Release.
5. Preserve the repository's existing version source and build-provenance checks; a Git Tag alone is not evidence of an executable or a successful test.

Where the branch model is `develop → main`, an integration commit on develop does not authorize a release from develop. Plan the promotion and release PR against the intended release baseline.

Use `draft-pull-request` or the repository's existing review/approval mechanisms as appropriate. Do not enable an unattended auto-merge that bypasses the release gate.

## Existing projects and historical tags

Inspect existing `git tag`, GitHub Releases, source-version fields and build receipts before bootstrapping. Version *numbers* must be inferred from actual state, not assumed to begin at `0.1.0`.

The [manifest bootstrapping documentation](https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md) describes `bootstrap-sha` and `.release-please-manifest.json`. Choose the last **actual release baseline** when initializing; distinguish it from internal checkpoint tags.

Git supports retrospectively adding an annotated tag to an existing commit; this doesn't rewrite the commit. Record the real source SHA and mark retrospective **development checkpoints** honestly. A retrospective tag is not evidence of a prior GitHub Release, shipped build, or historical approval. Before importing such tags into Release Please's version detection, check its actual tag matching and bootstrap behavior; avoid silently promoting checkpoint tags into published releases.

## Version-file integration

The `simple` release type's default version-file behavior must be checked against the target project's actual version source. For a Godot project (e.g. `application/config/version` in `project.godot`) or multiple synchronized Windows/build fields, keep the existing authoritative version field and configure or implement a **verified narrow updater** via supported Release Please mechanisms. Do not introduce an independent `version.txt` source of truth by accident. Prove the Release PR updates the correct files, and that its tag matches the built artifact and validation record.

## Validate before adoption

Exercise a representative dry-run or test repository and inspect the proposed Release PR for:
- `0.2.4 + feat → 0.2.5`
- `0.2.4 + breaking → 0.3.0`
- `1.2.4 + feat → 1.3.0`
- ten compatible features batched into a **single** release proposal
- correct manifest version, changelog, tag identity and release gate behavior.
