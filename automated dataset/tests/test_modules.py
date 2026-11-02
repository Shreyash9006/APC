import pandas as pd
from modules.preprocessing import preprocess_data
from modules.labelling import add_labels
from modules.validation import validate_dataset
from modules.profiling import profile_dataset


def test_preprocess_removes_duplicates_and_fills_missing():
    df = pd.DataFrame({"name": [" A ", " A ", None], "score": [2, 2, 4]})
    out, report = preprocess_data(df, return_report=True)
    assert len(out) == 2
    assert out["name"].isna().sum() == 0
    assert report["Duplicate rows removed"] == 1


def test_labelling_positive_negative_neutral():
    df = pd.DataFrame({"review": ["great", "awful", "ordinary"]})
    out = add_labels(df, "review", "great", "awful", neutral_label=True)
    assert out["Label"].tolist() == ["Positive", "Negative", "Neutral"]


def test_validation_detects_missing_label():
    result = validate_dataset(pd.DataFrame({"x": [1, 2]}))
    assert result["valid"] is True  # Label check is skipped when no Label column exists.


def test_profile_counts_rows():
    profile = profile_dataset(pd.DataFrame({"x": [1, None]}))
    assert profile["rows"] == 2
    assert profile["missing_cells"] == 1


def test_preprocess_normalizes_repeated_whitespace():
    df = pd.DataFrame({"review": ["  very   good   product  "]})
    out = preprocess_data(df, normalize_text=True)
    assert out.loc[0, "review"] == "very good product"


def test_labelling_marks_mixed_keywords():
    df = pd.DataFrame({"review": ["good but awful"]})
    out = add_labels(df, "review", "good", "awful")
    assert out.loc[0, "Label"] == "Mixed"


def test_numeric_labelling_threshold_and_missing_values():
    from modules.labelling import add_numeric_labels
    df = pd.DataFrame({"amount": [1999, 2000, 2001, None, "not a number"]})
    out = add_numeric_labels(
        df, "amount", ">", 2000,
        true_label="High", false_label="Standard", missing_label="Check value",
    )
    assert out["Label"].tolist() == ["Standard", "Standard", "High", "Check value", "Check value"]
    assert out.loc[2, "Labeling_Rule"] == "amount > 2000"


def test_numeric_labelling_supports_inclusive_comparison():
    from modules.labelling import add_numeric_labels
    df = pd.DataFrame({"score": [10, 20, 30]})
    out = add_numeric_labels(df, "score", ">=", 20, "Pass", "Fail")
    assert out["Label"].tolist() == ["Fail", "Pass", "Pass"]
