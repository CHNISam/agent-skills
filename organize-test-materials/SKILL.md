---
name: organize-test-materials
description: |
  整理测试产物到 agent-context/testing/ 目录。用于每轮测试结束后，
  将 report.pdf、defects.xlsx、improvements.md、截图录屏等材料归档到对应轮次。
  当用户说"整理测试材料"、"归档测试报告"、"测试产物放进去"时使用。
---

# 整理测试产物

## 目标结构

```
agent-context/testing/
├─ README.md
└─ round-N/
   ├─ *.pdf          ← 测试报告
   ├─ *.xlsx         ← 缺陷清单
   ├─ improvements.md  ← 改进建议
   └─ attachments/   ← 截图、录屏、补充材料
```

## 操作步骤

### 1. 确定轮次

- 检查 `agent-context/testing/` 下已有哪些 round-* 目录
- 新轮次 = 最大轮次 + 1
- 如果是第一次，轮次为 1

### 2. 创建目录

```bash
mkdir -p agent-context/testing/round-N/attachments
```

### 3. 移动/复制文件

根据用户提供的内容：

| 类型 | 目标文件名 | 说明 |
|------|-----------|------|
| 测试报告 | `*.pdf` | 用户提供的 report.pdf，可重命名为 `litemall-第N轮集成测试report.pdf` |
| 缺陷清单 | `*.xlsx` | 用户提供的缺陷Excel |
| 改进建议 | `improvements.md` | 用户提供的改进建议，如果是 markdown 直接放入，如果是其他格式（如 Word）转为 md 或原样放入 attachments |
| 截图录屏 | `attachments/*` | 全部放入 attachments 目录，不再细分 |

### 4. 更新 README

更新 `agent-context/testing/README.md`，在 round-N 行添加该轮的文件清单。

## 注意事项

- 不要创建 skills/ 目录
- 不要移动原型、PRD、测试用例等根目录文件
- attachments 作为本轮所有材料的统一目录，不再细分
- 如果用户只提供部分文件，只处理用户提供的部分
- 保持现有 round 目录不变，不合并
