# env-config.json schema

Place the manifest at `scripts/env-config.json` unless the target project already has a different convention.

```json
{
  "environments": {
    "dev": {
      "resourceAppid": "wx-dev-appid",
      "resourceEnv": "dev-cloudbase-env",
      "cloudDomin": "1234-dev-cloudbase-env-1234567890"
    },
    "prod": {
      "resourceAppid": "wx-prod-appid",
      "resourceEnv": "prod-cloudbase-env",
      "cloudDomin": "5678-prod-cloudbase-env-1234567890"
    }
  },
  "files": {
    "appConfig": "config.js",
    "projectConfig": "project.config.json",
    "cloudbaseConfig": "cloudbaserc.json",
    "cloudFunctionRoots": ["cloudfunctions"]
  },
  "scan": {
    "excludeDirectories": [".git", "node_modules", "miniprogram_npm"],
    "excludeFiles": ["scripts/env-config.json"],
    "reportOnlyFiles": ["README.md", "docs/environment.md"]
  }
}
```

## Field notes

- `environments`: arbitrary environment names are allowed. Use names that match the team's workflow, such as `dev`, `test`, `staging`, and `prod`.
- `resourceAppid`: WeChat miniprogram appid for that environment.
- `resourceEnv`: Tencent CloudBase/TCB environment ID.
- `cloudDomin`: cloud storage/resource domain when the app stores it explicitly.
- `files.appConfig`: JavaScript config file containing properties such as `resourceEnv` and `cloudDomin`.
- `files.projectConfig`: WeChat Developer Tools project config, usually `project.config.json`.
- `files.cloudbaseConfig`: CloudBase CLI config, usually `cloudbaserc.json`.
- `files.cloudFunctionRoots`: roots recursively scanned for `.js`, `.json`, and `.env` files that may contain env IDs or appids.
- `scan.excludeDirectories`: large/generated/vendor directories to skip.
- `scan.excludeFiles`: files that intentionally contain all environment values.
- `scan.reportOnlyFiles`: files that should report residual values without failing the switch.

## Adaptation checklist

1. Discover all currently used environment IDs, appids, and domains with `rg`.
2. Fill every configured environment before running the switcher.
3. Add any generated package directory to `excludeDirectories`.
4. Add documentation-only files to `reportOnlyFiles`.
5. Run check mode for every environment once to confirm no runtime residuals remain.
