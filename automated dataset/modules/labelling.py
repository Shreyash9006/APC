import pandas as pd


def _parse_terms(value):
    return [term.strip() for term in (value or "").split(",") if term.strip()]


def add_labels(
    df,
    column,
    positive_keywords,
    negative_keywords="",
    neutral_label=True,
    case_sensitive=False,
    mode="Multiple keyword rules",
):
    """Label rows with transparent positive/negative keyword rules."""
    if df is None:
        raise ValueError("No dataset was provided.")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    positive = _parse_terms(positive_keywords)
    negative = _parse_terms(negative_keywords)
    if not positive and not negative:
        raise ValueError("Enter at least one positive or negative keyword.")

    data = df.copy()
    text = data[column].fillna("").astype(str)
    if not case_sensitive:
        text = text.str.casefold()
        positive = [x.casefold() for x in positive]
        negative = [x.casefold() for x in negative]

    pos = text.map(lambda value: any(term in value for term in positive))
    neg = text.map(lambda value: any(term in value for term in negative))

    labels = []
    for p, n in zip(pos, neg):
        if p and n:
            labels.append("Mixed")
        elif p:
            labels.append("Positive")
        elif n:
            labels.append("Negative")
        else:
            labels.append("Neutral" if neutral_label else "Negative")

    data["Label"] = pd.Series(labels, index=data.index, dtype="string")
    data["Labeling_Rule"] = [
        "positive + negative" if p and n else
        "positive keyword" if p else
        "negative keyword" if n else
        "no keyword match"
        for p, n in zip(pos, neg)
    ]
    return data


def add_numeric_labels(
    df,
    column,
    operator,
    threshold,
    true_label="Above Threshold",
    false_label="At or Below Threshold",
    missing_label="Missing / Invalid",
):
    """Assign labels by comparing numeric values against a user-defined threshold.

    Supported operators: >, >=, <, <=, ==, !=. Original data is preserved;
    labels and the rule used are added as separate columns.
    """
    import operator as operator_module

    if df is None:
        raise ValueError("No dataset was provided.")
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")
    if operator not in {">", ">=", "<", "<=", "==", "!="}:
        raise ValueError("Unsupported comparison operator.")
    if not str(true_label).strip() or not str(false_label).strip():
        raise ValueError("Both matching and non-matching labels must be provided.")

    comparisons = {
        ">": operator_module.gt,
        ">=": operator_module.ge,
        "<": operator_module.lt,
        "<=": operator_module.le,
        "==": operator_module.eq,
        "!=": operator_module.ne,
    }
    data = df.copy()
    numeric_values = pd.to_numeric(data[column], errors="coerce")
    valid = numeric_values.notna()
    matched = pd.Series(False, index=data.index)
    matched.loc[valid] = comparisons[operator](numeric_values.loc[valid], float(threshold))

    labels = pd.Series(str(false_label).strip(), index=data.index, dtype="string")
    labels.loc[matched] = str(true_label).strip()
    if missing_label and str(missing_label).strip():
        labels.loc[~valid] = str(missing_label).strip()
    data["Label"] = labels
    data["Labeling_Rule"] = f"{column} {operator} {float(threshold):g}"
    data.loc[~valid, "Labeling_Rule"] = "missing or non-numeric value"
    return data
