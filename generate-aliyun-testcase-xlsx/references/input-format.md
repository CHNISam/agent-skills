# Input Format

Pass a JSON file to `scripts/generate_xlsx.py`.

## Command

```bash
python scripts/generate_xlsx.py --input draft.json --output output.xlsx
```

To use a different import template:

```bash
python scripts/generate_xlsx.py --input draft.json --output output.xlsx --template custom-template.xlsx
```

## JSON shape

```json
{
  "defaults": {
    "目录": "客户端微信小程序",
    "负责人": "aliyun5883078123",
    "优先级": "P1",
    "类型": "功能测试"
  },
  "cases": [
    {
      "标题": "入口页-入口展示-仅显示客户入口与司机入口",
      "前置条件": "应用已启动",
      "步骤描述": "进入入口页",
      "预期结果": "页面仅展示“客户入口”和“司机入口”两个主入口，文案为中文",
      "优先级": "P0"
    },
    {
      "标题": "服务点页-拒绝定位-支持城市切换与搜索选点",
      "前置条件": "首次进入服务点页",
      "步骤描述": "拒绝定位授权",
      "预期结果": "页面提供去设置、城市选择、搜索服务点入口",
      "优先级": "P0"
    }
  ]
}
```

## Supported keys

- `defaults`: Optional workbook-level defaults. These are applied first and can be overridden per case.
- `cases`: Required list of row objects.

Each case object can contain any of these keys:

- `标题`
- `目录`
- `负责人`
- `前置条件`
- `步骤描述`
- `预期结果`
- `关联需求`
- `优先级`
- `类型`
- `标签`
- `预计工时汇总`
- `实际工时汇总`

## Validation rules

- `标题` / `目录` / `负责人` / `前置条件` / `步骤描述` / `预期结果` / `优先级` / `类型` must not be empty after defaults are applied.
- `预计工时汇总` and `实际工时汇总` may be blank or numeric.
- `优先级` must be one of `P0`, `P1`, `P2`, `P3`.

## Practical workflow

1. Read the source materials.
2. Draft the cases in JSON using the headers above.
3. Run the generator.
4. Review the resulting workbook for omissions before handing it to the user.
