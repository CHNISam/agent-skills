---
name: cloud-github-auth-recovery
description: Use when GitHub access fails in an ephemeral cloud computer, gh reports missing authentication after a reset, or a signed-in browser works while Git or GitHub CLI does not.
---

# Cloud GitHub Auth Recovery

Recover the missing capability with the smallest authorized change. Browser sessions,
GitHub connectors, Git credentials, and `gh` authentication are separate.

## Diagnose before asking for another login

1. Identify the actual cloud shell and browser available now. Inspect the existing
   cloud browser's GitHub account first. Respect the user's chosen environment and
   excluded products; do not switch to their computer or launch another coding
   service to solve cloud authentication.
2. Verify `git` and `gh` exist and check their versions. Rediscover the worktree,
   configuration paths, and credential availability after a reset; historical paths,
   installed tools, and browser login do not prove current CLI readiness.
3. Check credential presence and selected account without exposing values. Use
   `gh auth status --hostname github.com`; never add `--show-token`, run
   `gh auth token`, print credential files, or dump the environment. Check only
   whether `GH_TOKEN`/`GITHUB_TOKEN` are set because they can override stored login.
4. Classify the actual error:
   - Missing/expired credentials: consider official authentication.
   - Read-only config path: select a permitted writable private location.
   - Network policy denial, DNS/TLS failure, or blocked API host: report the network
     blocker; another OAuth grant will not fix it.
   - Repository permission or SSO denial: verify the account and repository access;
     do not blindly replace a working login.

Stop a denied route. Do not tunnel, change hosts/proxies, extract connector tokens, or
use browser cookies to bypass restrictions. An independently authorized connector can
still perform supported repository work if that is allowed; disclose that native Git
remains unverified. Connector reads alone do not prove push, worktree, or test support.

## Prepare storage only when needed

Reuse an existing approved credential store when available. If the normal paths are
unwritable, discover a writable, access-restricted directory in the cloud workspace
outside every repository, shared folder, and published artifact. Keep its location
session-local; do not hard-code a previous task path into this skill.

- Set `GH_CONFIG_DIR` to a private configuration directory.
- If Git's global config is unwritable, set `GIT_CONFIG_GLOBAL` to a writable private
  file. This replaces the usual global config reads: check required identity,
  signing, and helper settings without dumping secret-bearing configuration.
- Do not copy credentials between browser, connector, accounts, or environments.
  Never commit auth files, device codes, tokens, or credential-bearing URLs.

Confirm the storage behavior before login: `gh` prefers a system credential store
but may fall back to plaintext. If secure storage is unavailable, disclose the
private-file fallback and obtain the required approval; do not silently opt into
`--insecure-storage`.

## Authorize once, then verify

When network access works and CLI authentication is genuinely missing, explain the
account, host, requested access, and storage. Obtain action-time user approval for
the new persistent grant. Start the official flow:

```sh
gh auth login --hostname github.com --git-protocol https --web
```

Reuse the already signed-in cloud browser at the official device page returned by
the CLI (normally https://github.com/login/device). Let the user approve the grant;
do not scrape session cookies or ask them to paste a token into chat. Request no
extra scopes without a demonstrated need and approval.

Keep one live login process/code. If it expires, stop that attempt; create one fresh
attempt only when the user is ready. Stop on a repeated failure or policy denial
and report the exact blocker instead of looping authorizations.

After approval, verify account and API access, then configure Git's helper with
`gh auth setup-git --hostname github.com` only within the approved storage/setup.
Verify a non-mutating read of the intended repository. A public clone or
`git ls-remote` can succeed anonymously; neither proves authenticated write access.
Verify writes only through the requested repository action, never a dummy push.

## Resume and report precisely

Read repository instructions and preserve other writers' branches and uncommitted
work. Resume only the originally authorized action; authentication is not permission
to merge, overwrite history, or change unrelated settings.

Report: browser account checked; CLI/API/Git capability actually verified; storage
mode; remaining blocker; and the task result. CI checks prove only their tested
scope, not full product acceptance or cloud-auth recovery.

A reset after one or two days is a hypothesis unless the platform documents it.
This skill makes recovery repeatable; it cannot guarantee credential persistence
or prevent the next environment reset.

## Official references

- [GitHub CLI login and credential storage](https://cli.github.com/manual/gh_auth_login)
- [GitHub CLI environment variables](https://cli.github.com/manual/gh_help_environment)
- [Git environment variables](https://git-scm.com/docs/git)
