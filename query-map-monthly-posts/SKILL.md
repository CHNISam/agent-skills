---
name: query-map-monthly-posts
description: Safely query monthly 温暖拍 and 设施拍 counts for named users in the map-miniprogram CloudBase MySQL database. Use when asked for per-user monthly post statistics, especially production read-only checks requiring temporary dev/prod switching, environment verification, and restoration.
---

# Query Map Monthly Posts

Return concise per-user counts while keeping production access read-only and restoring the default environment.

## Definitions

- Table: `map_suihsoupai`; user table: `map_user`.
- Join: `map_user._id = map_suihsoupai.user_id`.
- 温暖拍: trimmed `type = '2'`.
- 设施拍: trimmed `type IN ('0', '1')`.
- Exclude rows where `is_deleted = 1`.
- Interpret a month as the half-open interval `[month start, next month start)` using `FROM_UNIXTIME(createdAt / 1000)`.
- This statistic counts随手拍 records only. Do not include `map_poi_evaluation` unless the user explicitly requests the plaza's combined feed definition.

## Workflow

1. Resolve the requested year, month, and exact user names. Use the current year only when context makes it unambiguous.
2. Before any production operation, obtain explicit user approval immediately before execution. Treat a direct request such as “去 prod 查……” as approval for that read-only query. Never infer approval from older, unrelated turns.
3. Inspect the active mcporter source with `npx.cmd mcporter list`. On Codex it normally reads `~/.codex/config.toml`; do not assume Claude's settings control it.
4. Check authentication and the active environment:

   ```powershell
   npx.cmd mcporter call cloudbase.auth action=status --output json
   ```

   Stop for login if `auth_status` is not `READY`.
5. If needed, temporarily change `CLOUDBASE_ENV_ID` to `prod-6gv6kwxe65437245` in the actual mcporter source. Preserve UTF-8 without BOM. If keeping both clients aligned, update `C:\Users\Administrator\.claude\settings.json` too.
6. Run `auth status` again and continue only when `current_env_id` exactly equals `prod-6gv6kwxe65437245`.
7. Execute only `cloudbase.queryMysqlDatabase action=runQuery`. Never use a statement/write tool for this task.
8. Use this query, replacing dates and escaped names:

   ```sql
   SELECT
     u._id AS user_id,
     u.name,
     SUM(CASE WHEN TRIM(s.type) = '2' THEN 1 ELSE 0 END) AS warm_count,
     SUM(CASE WHEN TRIM(s.type) IN ('0', '1') THEN 1 ELSE 0 END) AS facility_count
   FROM map_user u
   LEFT JOIN map_suihsoupai s
     ON u._id = s.user_id
    AND FROM_UNIXTIME(s.createdAt / 1000) >= '<YYYY-MM-01 00:00:00>'
    AND FROM_UNIXTIME(s.createdAt / 1000) < '<NEXT-MONTH-01 00:00:00>'
    AND (s.is_deleted != 1 OR s.is_deleted IS NULL)
   WHERE u.name IN ('<NAME_1>', '<NAME_2>')
   GROUP BY u._id, u.name
   ORDER BY u.name, u._id;
   ```

9. If one name maps to multiple user IDs, do not silently merge them. Report the ambiguity or list each ID separately.
10. Restore `dev-5gzz7rxdbcf5d7dc` in every modified config even if the query fails, then verify `auth status` reports dev.
11. Report only the requested month. Default format:

   ```text
   <month>：
   - <name>: 温暖拍 <n>，设施拍 <n>
   ```

## Safety

- Production access is read-only for this skill.
- Do not expose OpenIDs, credentials, full config contents, or unrelated rows.
- Do not leave any client configured for prod.
- Do not reuse a previous month's result when the user changes the month.
