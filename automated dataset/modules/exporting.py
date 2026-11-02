from io import BytesIO


def dataframe_to_excel(df):
    """Serialize a DataFrame to an in-memory Excel workbook."""
    buffer = BytesIO()
    with __import__("pandas").ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dataset")
    return buffer.getvalue()


def report_to_text(result):
    lines = [
        "AUTOMATED DATASET STUDIO — VALIDATION REPORT",
        "=" * 48,
        f"Overall status: {'PASS' if result.get('valid') else 'ISSUES FOUND'}",
        f"Checks passed: {result.get('passed', 0)}",
        f"Checks failed: {result.get('failed', 0)}",
        "",
    ]
    for item in result.get("checks", []):
        lines.append(f"[{'PASS' if item['passed'] else 'FAIL'}] {item['name']}: {item['message']}")
    return "\n".join(lines) + "\n"
