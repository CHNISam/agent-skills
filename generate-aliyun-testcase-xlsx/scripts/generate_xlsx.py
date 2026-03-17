#!/usr/bin/env python3

import argparse
import copy
import json
import re
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"a": NS_MAIN, "r": NS_REL}
ET.register_namespace("", NS_MAIN)

HEADERS = [
    "标题",
    "目录",
    "负责人",
    "前置条件",
    "步骤描述",
    "预期结果",
    "关联需求",
    "优先级",
    "类型",
    "标签",
    "预计工时汇总",
    "实际工时汇总",
]

REQUIRED_FIELDS = {
    "标题",
    "目录",
    "负责人",
    "前置条件",
    "步骤描述",
    "预期结果",
    "优先级",
    "类型",
}

NUMERIC_FIELDS = {"预计工时汇总", "实际工时汇总"}
ALLOWED_PRIORITIES = {"P0", "P1", "P2", "P3"}


def qname(tag):
    return f"{{{NS_MAIN}}}{tag}"


def col_letter(index):
    letters = []
    while index:
        index, remainder = divmod(index - 1, 26)
        letters.append(chr(65 + remainder))
    return "".join(reversed(letters))


def read_cell_text(cell):
    if cell is None:
        return ""
    if cell.attrib.get("t") == "inlineStr":
        return "".join((node.text or "") for node in cell.iterfind(".//a:t", NS))
    value = cell.find("a:v", NS)
    return "" if value is None or value.text is None else value.text


def load_payload(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object.")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Input JSON must contain a non-empty 'cases' list.")
    defaults = data.get("defaults", {})
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        raise ValueError("'defaults' must be an object when provided.")
    return defaults, cases


def coerce_numeric(value, field_name):
    if value in ("", None):
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
            return int(text) if text.isdigit() or (text.startswith("-") and text[1:].isdigit()) else float(text)
    raise ValueError(f"Field '{field_name}' must be blank or numeric.")


def normalize_case(case, defaults, index):
    if not isinstance(case, dict):
        raise ValueError(f"Case #{index} must be an object.")

    row = {}
    for header in HEADERS:
        value = case.get(header, defaults.get(header, ""))
        if header in NUMERIC_FIELDS:
            row[header] = coerce_numeric(value, header)
        else:
            row[header] = "" if value is None else str(value).strip()

    missing = [field for field in REQUIRED_FIELDS if not row[field]]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Case #{index} is missing required fields: {missing_text}")

    if row["优先级"] not in ALLOWED_PRIORITIES:
        allowed = ", ".join(sorted(ALLOWED_PRIORITIES))
        raise ValueError(f"Case #{index} has invalid 优先级 '{row['优先级']}'. Allowed: {allowed}")

    return row


def resolve_sheet_path(template_zip):
    workbook = ET.fromstring(template_zip.read("xl/workbook.xml"))
    rels = ET.fromstring(template_zip.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets = workbook.find("a:sheets", NS)
    if sheets is None or not list(sheets):
        raise ValueError("Template workbook has no worksheets.")
    first_sheet = list(sheets)[0]
    rel_id = first_sheet.attrib[f"{{{NS_REL}}}id"]
    return rel_map[rel_id].lstrip("/")


def load_template_rows(sheet_root):
    sheet_data = sheet_root.find("a:sheetData", NS)
    if sheet_data is None:
        raise ValueError("Template sheet is missing sheetData.")

    rows = sheet_data.findall("a:row", NS)
    if len(rows) < 2:
        raise ValueError("Template sheet must contain a header row and one sample body row.")

    header_row = copy.deepcopy(rows[0])
    body_row = copy.deepcopy(rows[1])
    header_values = [read_cell_text(cell) for cell in header_row.findall("a:c", NS)]
    if header_values != HEADERS:
        expected = " | ".join(HEADERS)
        actual = " | ".join(header_values)
        raise ValueError(f"Template header mismatch.\nExpected: {expected}\nActual: {actual}")
    return sheet_data, header_row, body_row


def make_inline_string(cell, text):
    cell.set("t", "inlineStr")
    inline = ET.SubElement(cell, qname("is"))
    node = ET.SubElement(inline, qname("t"))
    if text != text.strip() or "\n" in text:
        node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    node.text = text


def render_row(body_row, row_number, values):
    row_attrib = {key: value for key, value in body_row.attrib.items() if key != "r"}
    row_attrib["r"] = str(row_number)
    row = ET.Element(qname("row"), row_attrib)

    template_cells = body_row.findall("a:c", NS)
    if len(template_cells) < len(HEADERS):
        raise ValueError("Template body row does not contain all expected columns.")

    for index, header in enumerate(HEADERS, start=1):
        template_cell = template_cells[index - 1]
        cell = ET.Element(qname("c"))
        cell.set("r", f"{col_letter(index)}{row_number}")
        style_id = template_cell.attrib.get("s")
        if style_id is not None:
            cell.set("s", style_id)

        value = values[header]
        if value == "":
            row.append(cell)
            continue

        if header in NUMERIC_FIELDS:
            cell.set("t", "n")
            node = ET.SubElement(cell, qname("v"))
            node.text = str(value)
        else:
            make_inline_string(cell, str(value))

        row.append(cell)

    return row


def replace_sheet_data(sheet_root, rows):
    sheet_data, header_row, body_row = load_template_rows(sheet_root)
    for child in list(sheet_data):
        sheet_data.remove(child)

    sheet_data.append(header_row)
    for offset, values in enumerate(rows, start=2):
        sheet_data.append(render_row(body_row, offset, values))

    dimension = sheet_root.find("a:dimension", NS)
    if dimension is None:
        dimension = ET.Element(qname("dimension"))
        sheet_root.insert(0, dimension)
    last_row = len(rows) + 1
    dimension.set("ref", f"A1:{col_letter(len(HEADERS))}{last_row}")


def write_output(template_path, output_path, sheet_path, sheet_root):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    xml_bytes = ET.tostring(sheet_root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(template_path, "r") as source, zipfile.ZipFile(output_path, "w") as target:
        for item in source.infolist():
            data = xml_bytes if item.filename == sheet_path else source.read(item.filename)
            target.writestr(item, data)


def main():
    parser = argparse.ArgumentParser(description="Generate an Aliyun manual-import testcase workbook.")
    parser.add_argument("--input", required=True, help="Path to the JSON case definition file.")
    parser.add_argument("--output", required=True, help="Path to the generated xlsx file.")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parent.parent / "assets" / "aliyun-manual-import-template.xlsx"),
        help="Path to the source template workbook.",
    )
    args = parser.parse_args()

    template_path = Path(args.template).resolve()
    output_path = Path(args.output).resolve()
    if template_path == output_path:
        raise ValueError("Output path must be different from the template path.")
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    defaults, raw_cases = load_payload(args.input)
    rows = [normalize_case(case, defaults, index) for index, case in enumerate(raw_cases, start=1)]

    with zipfile.ZipFile(template_path, "r") as template_zip:
        sheet_path = resolve_sheet_path(template_zip)
        sheet_root = ET.fromstring(template_zip.read(sheet_path))

    replace_sheet_data(sheet_root, rows)
    write_output(template_path, output_path, sheet_path, sheet_root)

    titles = [row["标题"] for row in rows]
    duplicates = sorted({title for title in titles if titles.count(title) > 1})
    result = {
        "status": "ok",
        "output": str(output_path),
        "case_count": len(rows),
        "duplicate_titles": duplicates,
        "template": str(template_path),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
