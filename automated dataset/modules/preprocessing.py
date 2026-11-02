import re
import pandas as pd


def preprocess_data(
    df,
    remove_duplicates=True,
    drop_empty_rows=True,
    trim_text=True,
    normalize_columns=False,
    normalize_text=True,
    numeric_strategy="Median",
    text_strategy="Fill with Unknown",
    return_report=False,
):
    """Configurable, non-destructive data-cleaning pipeline."""
    if df is None:
        raise ValueError("No dataset was provided.")
    if len(df.columns) == 0:
        raise ValueError("The dataset has no columns.")

    data = df.copy()
    original_rows = len(data)
    original_columns = len(data.columns)
    original_missing = int(data.isna().sum().sum())

    data.columns = data.columns.astype(str).str.strip()
    if normalize_columns:
        data.columns = [
            re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", col)).strip("_").lower()
            or f"column_{i + 1}"
            for i, col in enumerate(data.columns)
        ]
    if data.columns.duplicated().any():
        raise ValueError("Column names are duplicated after cleaning. Rename columns and retry.")

    if trim_text:
        for col in data.select_dtypes(include=["object", "string"]).columns:
            data[col] = data[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    if normalize_text:
        for col in data.select_dtypes(include=["object", "string"]).columns:
            data[col] = data[col].map(
                lambda x: re.sub(r"\s+", " ", x).strip() if isinstance(x, str) else x
            )

    if drop_empty_rows:
        data = data.dropna(how="all")
    removed_empty = original_rows - len(data)

    removed_duplicates = 0
    if remove_duplicates:
        before = len(data)
        data = data.drop_duplicates()
        removed_duplicates = before - len(data)

    for col in data.columns:
        if not data[col].isna().any():
            continue
        if pd.api.types.is_numeric_dtype(data[col]):
            if numeric_strategy == "Median":
                fill_value = data[col].median()
            elif numeric_strategy == "Mean":
                fill_value = data[col].mean()
            elif numeric_strategy == "Zero":
                fill_value = 0
            else:
                continue
            if pd.isna(fill_value):
                continue
            data[col] = data[col].fillna(fill_value)
        else:
            if text_strategy == "Fill with Unknown":
                data[col] = data[col].fillna("Unknown")
            elif text_strategy == "Fill with empty text":
                data[col] = data[col].fillna("")
    data = data.reset_index(drop=True)

    report = {
        "Rows before": original_rows,
        "Rows after": len(data),
        "Columns": original_columns,
        "Empty rows removed": removed_empty,
        "Duplicate rows removed": removed_duplicates,
        "Missing cells before": original_missing,
        "Missing cells after": int(data.isna().sum().sum()),
    }
    return (data, report) if return_report else data
