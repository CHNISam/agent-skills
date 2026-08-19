---
name: shmedia-onboard-district
description: Onboard a new Shanghai district media app (media-basic-port API family) into ShMediaRewardAdapter -- capture credentials, handle protocol quirks, wire into GitHub Actions, verify with a real cloud run. Use when adding a new district (e.g. 虹口/长宁/静安/黄浦/宝山/崇明/徐汇) to this repo's reward-portfolio project, or when a similar config-driven adapter needs a new tenant onboarded the same way.
---

# Onboard a new ShMedia district

This repo already proved 上海杨浦, 上海嘉定, 上海宝山, 上海徐汇, and 上海
虹口 on the same `ShMediaRewardAdapter` (see `adapters/shmedia/client.py`,
`README.md`). Onboarding another district (remaining candidates from
`xiaobu689/HhhhScripts` `reads/`: 崇明, 长宁, 静安, 黄浦) should be cheap --
config, not new code -- if you follow this order. Don't skip steps or
declare success from local-only evidence; the whole point of this repo is
that a "done" claim means a real server confirmed it.

Pattern so far, 4 of 5 districts: the reference script's `Host` header is
stale and the real API host only surfaces from live traffic (嘉定, 宝山,
徐汇, 虹口 all differed; only 杨浦's reference host was accurate). Treat
this as the expected case, not the exception -- budget for one
capture-restart round trip.

## 0. Preconditions
- User already has a logged-in account/app for the target district. If
  not, that's their one required manual step (register/real-name/SMS) --
  ask, don't assume.
- **Technical feasibility isn't the only Kill criterion.** 上海黄浦 was
  technically capturable (no pinning, real host found, personal/* traffic
  already flowing) but got Killed mid-capture anyway because its points
  can't be redeemed for anything -- the user checked the app's reward/mall
  section themselves. If the user says a district's points are
  unredeemable, stop immediately regardless of how far along the capture
  is; don't finish it "since it's already working." This can't be checked
  by traffic inspection alone -- it's the user's call, ask if unsure.
- `.venv` and `tools/capture_shmedia.py` already exist in this repo.
  Starting mitmdump (`0.0.0.0:8080` listener) requires the user's explicit
  in-session authorization each time -- the safety classifier blocks it by
  default and conversational "I already said yes earlier" does not carry
  across unrelated tool categories. Ask plainly if a fresh block appears.

## 1. Protocol archaeology first -- don't reverse-engineer from scratch
```
gh api "repos/xiaobu689/HhhhScripts/contents/reads/上海<district>/上海<district>.py" --jq '.content' | base64 -d
```
Read it for: API host(s), header names (`token`, `deviceId`?, `siteId`?),
whether `score/info` needs extra body fields, the read-channel id used for
`news/content/list`. **Treat the host in the reference script as a
hypothesis, not a fact** -- 嘉定's actual host (`shjdapp.jcmc.sh.cn`) did
not match its reference script (`jdapi.shmedia.tech`) at all; the real
host only surfaced from live captured traffic. Don't hardcode the
reference script's host as truth.

## 2. Add the host to the capture script
In `tools/capture_shmedia.py`:
- Add `"<real-or-guessed-host>": "上海<district>"` to `KNOWN_HOSTS`.
- **Always add a `SITE_TEMPLATES["上海<district>"]` entry with
  `read_channel_ids` from step 1, even if the district has no other
  quirks.** `read_channel_ids` is never discoverable from captured
  headers -- skipping this (as happened onboarding 上海宝山) silently
  produces a working-looking capture whose read task never runs
  (`config.read_channel_ids` empty → read step skipped, no error, just a
  quietly lower `points_delta` than it should be). Only add
  `score_info_extra_body` if step 1 actually showed the district needs it.
  These seed a *new* account entry only, never overwrite captured secrets.
- `PROOF_PATHS` usually doesn't need changes (`score/info`, `score/total`,
  `personal/get` already covered) -- only add a path if the district's
  score endpoint is genuinely different.

## 3. Capture (mostly automatic, minimal human step)
1. Confirm port 8080 free (`netstat -ano | grep ":8080 " | grep LISTENING`), clear stale `data/capture_done.flag`.
2. Start: `"$VENV/Scripts/mitmdump.exe" --listen-host 0.0.0.0 --listen-port 8080 -s tools/capture_shmedia.py > data/mitmdump.log 2>&1` (background).
3. If the phone's proxy/CA trust from a previous district is still set, the user only needs to open the target app and let it load -- no re-setup. Otherwise walk them through: set Wi-Fi proxy to this machine's LAN IP:8080, visit `http://mitm.it`, install+trust the cert.
4. Poll for `data/capture_done.flag` (Monitor with an until-loop, not manual sleep-polling).
5. **If the host in KNOWN_HOSTS doesn't match live traffic** (grep `data/mitmdump.log` for the district's real domain), that's normal -- update KNOWN_HOSTS and restart mitmdump, ask the user to just refresh once more. This happened with 嘉定 and cost one extra round trip; expect it.
6. If you see `Client TLS handshake failed ... does not trust the proxy's certificate` for the target host even with the CA trusted: that's certificate pinning. Stop, tell the user to turn the proxy off immediately (it breaks the app's own traffic while active), and Kill that district -- do not reach for Frida/objection/jailbreak bypass tooling. Document the Kill in README same as 上海普陀's first attempt.
7. **Pinning being gone on retry doesn't mean capture will succeed** -- 上海普陀's second attempt (2026-08-18) had zero pinning, but its reward UI had migrated entirely off `media-basic-port/personal/score/*` onto a `mall-api.<host>` member/goods/trade-service backend our `PROOF_PATHS` don't recognize. If the target app's "我的"/积分 entry point routes to hosts/paths outside `KNOWN_HOSTS`+`PROOF_PATHS` no matter how much the user navigates, that's a different API family, not a config tweak -- needs fresh protocol reverse-engineering (bigger scope) or a Kill, not more retries of the same navigation.

## 4. Verify locally before touching CI
```
"$VENV/Scripts/python.exe" tools/smoke_test.py 上海<district>
```
Expect `points_delta >= 0` and `status: "ok"`. If it fails with a protocol
error, that's real information (missing body field, wrong header, wrong
host) -- read `ShMediaProtocolError`'s `failed_endpoint`/`response_body`
and fix `SiteConfig`/`client.py` generically (a new *optional* field other
sites default away from), not with district-specific branches.

If `status: "ok"` but `tasks_completed` is missing `"read"` and
`points_delta` looks lower than expected: check `read_channel_ids` in the
captured `config/accounts.json` entry isn't empty (see step 2's warning).
`status: "ok"` with an incomplete task list is a silent gap, not an error
-- it won't show up unless you actually look at `tasks_completed`.

**Regression-check the already-live district(s) immediately after any
client.py change** (`tools/smoke_test.py 上海杨浦` etc.) -- a change made
for the new district must not touch existing production behavior.

## 5. Wire into GitHub Actions
1. In `adapters/shmedia/run.py`, add an entry to `SITE_ENV_REGISTRY` with a
   unique `env_prefix` (e.g. `SHHK` for 虹口) and the non-secret defaults
   (base_url, site_id, user_agent, read_channel_ids, score_info_extra_body).
2. Push the real captured token/device_id straight into GitHub Secrets
   without ever printing them:
   ```
   "$VENV/Scripts/python.exe" -c "import json;print(json.load(open('config/accounts.json',encoding='utf-8'))['accounts'][N]['token'],end='')" | gh secret set SH<PREFIX>_TOKEN --repo <owner>/<repo>
   ```
   (same for `_DEVICE_ID`; empty string is fine for tenants without one).
   Verify with `gh secret list` (names/timestamps only -- never echo values).
3. Add the two env lines to `.github/workflows/shmedia-daily.yml`'s existing
   "Run ShMediaRewardAdapter" step.

## 6. Real cloud verification -- mandatory, not optional
```
gh workflow run shmedia-daily.yml --repo <owner>/<repo>
gh run watch <run-id> --repo <owner>/<repo> --exit-status
```
Then pull actual numbers, don't just trust the green checkmark:
```
gh run view <run-id> --repo <owner>/<repo> --log | grep -E "总积分|完成任务|积分变化"
```
A local pass is not sufficient evidence -- `data/` not existing on a fresh
checkout caused a real first-run failure for 上海杨浦 that local testing
never caught. Expect the first cloud run might fail for a boring
environment reason; fix and re-run until the run log shows a real
`points_delta` and the job is green.

## 7. Document and commit
- Update `README.md`'s district status table with Keep/Kill and evidence
  (real points before/after, run URL).
- `.venv/Scripts/python.exe -m unittest discover -s tests -v` must pass.
- Add tests for any new SiteConfig field/quirk (see `TestJiadingQuirks` in
  `tests/test_client.py` for the pattern: mock at the `session.post` level,
  assert on headers/body, no network).
- One commit for the adapter/CI changes, git push -- don't leave it staged.

## What NOT to do
- Don't guess a district's host/quirks and skip live verification.
- Don't add per-district `if site_name == "..."` branches in `client.py` --
  express the difference as `SiteConfig` data.
- Don't reach for pinning-bypass tooling (Frida/objection/jailbreak) when a
  district turns out to pin certs -- Kill it and document why, same as
  上海普陀.
- Don't declare a district "live" from a local smoke test alone -- the
  GitHub Actions run is the actual unattended path users depend on.
