import pandas as pd


def validate_dataset(df):
    """Run a set of transparent dataset quality checks."""
    checks = []

    def add(name, passed, message):
        checks.append({"name": name, "passed": bool(passed), "message": message})

    if df is None:
        add("Dataset exists", False, "No dataset was supplied.")
        return _result(checks)

    add("Dataset not empty", not df.empty, f"{len(df):,} rows found.")
    add("Has columns", len(df.columns) > 0, f"{len(df.columns):,} columns found.")
    add(
        "Unique column names",
        not df.columns.duplicated().any(),
        "Column names are unique." if not df.columns.duplicated().any()
        else "Duplicate column names exist.",
    )
    duplicate_count = int(df.duplicated().sum()) if not df.empty else 0
    add(
        "No duplicate rows",
        duplicate_count == 0,
        "No duplicate rows found." if duplicate_count == 0
        else f"{duplicate_count:,} duplicate rows found.",
    )
    missing_count = int(df.isna().sum().sum())
    add(
        "No missing values",
        missing_count == 0,
        "No missing values found." if missing_count == 0
        else f"{missing_count:,} missing cells found.",
    )
    if "Label" in df.columns:
        allowed = {"Positive", "Negative", "Neutral", "Mixed"}
        actual = set(df["Label"].dropna().astype(str).unique())
        invalid = sorted(actual - allowed)
        no_missing_labels = not df["Label"].isna().any()
        add(
            "Labels valid",
            not invalid and no_missing_labels,
            "Labels are from the supported set." if not invalid and no_missing_labels
            else f"Invalid labels: {invalid or 'missing label values'}.",
        )
    else:
        add("Label column", True, "No Label column found; label check skipped.")

    return _result(checks)


def _result(checks):
    passed = sum(item["passed"] for item in checks)
    failed = len(checks) - passed
    return {
        "valid": failed == 0,
        "checks": checks,
        "passed": passed,
        "failed": failed,
        "messages": [item["message"] for item in checks],
    }
