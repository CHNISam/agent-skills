---
name: cloudbase-datamodel
description: 在 CloudBase（腾讯云开发）上创建/迁移/修复 MySQL 数据模型，并在 Windows 上可靠地调用 cloudbase MCP 工具。当需要用 Mermaid 建数据模型、把旧表数据迁移到新模型、排查"数据模型一打开就报 UnknownColumn / 数据异常"、或在 Windows(PowerShell/Git Bash) 下用 mcporter 传复杂 SQL/JSON 参数时使用。连接与切换环境见 tcb-connect。
---

# CloudBase MySQL 数据模型操作

连接、环境切换、prod 操作规范见 **tcb-connect** skill。本 skill 只讲**数据模型**特有的坑和工作流。

## 0. Windows 上可靠调用 mcporter（关键前置）

Windows 上 `npx.cmd mcporter call ... --args '{json}'` 会被 cmd.exe 二次分词破坏（典型报错 `'C:\Program' is not recognized` 或 `Bad escaped character in JSON`）。**绕过 .cmd 包装，直接用 node 调 cli.js**：

```bash
# 定位 mcporter 入口（npx 缓存里，hash 目录会变，动态查）
MCP=$(find "$LOCALAPPDATA/npm-cache/_npx" -path "*mcporter/dist/cli.js" 2>/dev/null | head -1)
# 简单参数：key=value 可直接用
node "$MCP" call cloudbase.manageDataModel action=list --output json
```

**复杂参数（含中文 <<注释>>、嵌套引号、空字符串、多语句）→ 写 JSON 文件再 `--args "$(cat 文件)"`**，避免任何 shell 转义地狱。注意 Git Bash 的 `/tmp` 与 Windows python 的 `/tmp` 不是同一处，用显式 Windows 临时路径：

```bash
TMPD="$LOCALAPPDATA/Temp"
python build_args.py            # 用 python json.dump 生成 args，最稳
node "$MCP" call cloudbase.modifyDataModel --args "$(cat "$TMPD/args.json")" --output json
```

写完务必 `python -c "import json;json.load(open(...))"` 验 JSON 合法再调用。

## 1. 数据模型的三个硬约束（务必先记住）

1. **数据模型依赖一套系统列**：`_id`(varchar(34), 主键)、`_openid`、`owner`、`_mainDep`、`createdAt`(bigint)、`updatedAt`(bigint)、`createBy`、`updateBy`。**用原生 DDL `CREATE TABLE` 建的表只有业务列，缺这些系统列**，控制台一打开模型就 `FailedOperation.UnknownColumn`（先报 `createdAt`，再报 `_id in order clause`）。
2. **模型里的 `datetime` 字段，MySQL 底层是 bigint 毫秒时间戳**，不是原生 `datetime`。建成原生 `datetime` → 控制台该列显示「数据异常」。
3. **`modifyDataModel` 只支持 `action=create`**，不支持更新/覆盖（同名再 create 报 `数据模型全局唯一`）。MCP/SQL **都没有改模型字段、删字段、删模型的能力** —— 这些只能在控制台（模型配置）手动做。

## 2. 正确建模工作流

**优先让 `modifyDataModel` 自己建物理表**（它会自动带齐系统列、datetime 存成 bigint）。不要先手写 DDL 建表再补模型。

```bash
# mermaid 写进 JSON（python 生成），datetime 字段直接写 datetime 类型即可，底层自动 bigint
node "$MCP" call cloudbase.modifyDataModel --args "$(cat "$TMPD/model_args.json")" --output json
# args 形如: {"mermaidDiagram":"classDiagram\nclass X {...}", "action":"create",
#            "dbInstanceType":"MYSQL", "publish":true}
```

Mermaid 字段语法：`字段名: 类型 = 默认值 <<中文标题>>`，约束用 `required()["a"]` / `unique()["a"]` / `display_field() "a"`，模型标题用 `note for X "标题"`。**不要在 mermaid 里手加 `created_at`/`updated_at`**——会和系统自动的 `createdAt`/`updatedAt` 重复，控制台出现两列「创建时间」。

建完**必须** `manageDataModel action=get name=X` 验证字段，并查一条数据确认能读。

## 3. 救场：表已用原生 DDL 建好、模型打不开

若物理表已存在（业务列齐但缺系统列），按 CloudBase 原生结构重建表，再让模型绑定。参照已有的原生模型表（如 `map_admin`）的列结构与类型：

```sql
-- 系统列(全 nullable，类型照抄 map_admin) + 业务列 + _id 主键 + 业务唯一键
CREATE TABLE `X` (
  `owner` varchar(256) NULL, `_mainDep` varchar(64) NULL,
  `createdAt` bigint NULL, `createBy` varchar(256) NULL, `updateBy` varchar(256) NULL,
  `_openid` varchar(256) NULL, `_id` varchar(34) NOT NULL, `updatedAt` bigint NULL,
  -- ...业务列...
  PRIMARY KEY (`_id`), UNIQUE KEY `uniq_biz` (`业务主键`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

用 `manageSqlDatabase action=initializeSchema statements=[...]` 跑有序的 DROP/CREATE/INSERT。重建前先把数据捞出来（见 tcb-connect 备份脚本），重建后回插，回插时要自己生成 `_id`（随机 20+ 字符）、`_openid`、`createdAt`/`updatedAt`(epoch ms)。

> 验证："控制台同款查询" `SELECT _id, createdAt, ... ORDER BY _id` 不报错 + "云函数同款查询" 都过，才算修好。

## 4. 旧表数据迁移到新模型表

幂等迁移，字段映射 + null 兜底。注意原生 CloudBase 表列名可能是驼峰大小写（如 `openID`），MySQL 列名大小写不敏感可兼容 `openid`：

```sql
INSERT INTO new_tbl (openid, name, enabled, created_at, updated_at)
SELECT openID, name, IFNULL(enabled,1), NOW(), NOW()
FROM old_tbl WHERE openID IS NOT NULL AND CHAR_LENGTH(openID) > 0
ON DUPLICATE KEY UPDATE name=VALUES(name), enabled=VALUES(enabled), updated_at=NOW();
```

(空串判断用 `CHAR_LENGTH()>0` 而非 `<>''`，省去 JSON 里 `''` 的多层转义。)

## 5. 删模型里多余字段（只能控制台）

MCP 删不了。控制台：右上「模型配置」→ 找到要删的字段 → 删除 → 保存发布。控制台删字段后物理列会被软重命名为 `字段名-drop-<时间戳>`（数据不会立刻丢，但模型不再引用）。**别用 SQL 直接 drop 物理列**——模型元数据还引用着，会重新报「未知字段/数据异常」。

## 排查速查

| 现象 | 原因 | 解决 |
|------|------|------|
| `'C:\Program' is not recognized` / `Bad escaped character in JSON` | npx.cmd 经 cmd.exe 破坏 JSON 参数 | 用 `node <cli.js>`，复杂参数走 JSON 文件 |
| 模型打开报 `UnknownColumn 'createdAt'` / `'_id'` | 原生 DDL 表缺系统列 | 按 §3 重建为 CloudBase 原生结构 |
| 某列显示「数据异常」 | datetime 字段建成了原生 datetime | `ALTER MODIFY col bigint` + UPDATE 写 epoch ms |
| 两列「创建/更新时间」 | mermaid 手加了 created_at/updated_at，和系统列重复 | §5 控制台删掉自定义那两列 |
| 同名 create 报 `数据模型全局唯一` | modifyDataModel 不支持覆盖更新 | 改字段只能控制台；要换结构得控制台删模型后重建 |
