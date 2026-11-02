import pandas as pd


def profile_dataset(df):
    """Return useful, compact profiling information for a DataFrame."""
    missing = df.isna().sum()
    profile = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data type": [str(dtype) for dtype in df.dtypes],
        "Non-null": [int(x) for x in df.notna().sum()],
        "Missing": [int(x) for x in missing],
        "Missing %": [(float(x) / len(df) * 100) if len(df) else 0 for x in missing],
        "Unique values": [int(df[col].nunique(dropna=True)) for col in df.columns],
    })
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(missing.sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_profile": profile,
        "missing_by_column": missing,
    }
