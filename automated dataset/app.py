import hashlib
import os
from io import BytesIO

import pandas as pd
import streamlit as st

from modules.preprocessing import preprocess_data
from modules.labelling import add_labels, add_numeric_labels
from modules.validation import validate_dataset
from modules.profiling import profile_dataset
from modules.exporting import dataframe_to_excel, report_to_text

st.set_page_config(
    page_title="Automated Dataset Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    try:
        with open(css_path, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    except OSError:
        pass

load_css()

for key, default in {
    "source_df": None,
    "processed_df": None,
    "labelled_df": None,
    "validation_result": None,
    "file_signature": None,
    "source_name": None,
    "history": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.markdown("# ◈ Dataset Studio")
    st.caption("Automated data preparation workspace")
    page = st.radio(
        "WORKSPACE",
        ["Overview", "Upload & Explore", "Preprocessing", "Labelling", "Validation", "Compare Versions", "Export"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**Workflow status**")
    steps = [
        ("Dataset uploaded", st.session_state.source_df is not None),
        ("Data processed", st.session_state.processed_df is not None),
        ("Labels created", st.session_state.labelled_df is not None),
        ("Validation run", st.session_state.validation_result is not None),
    ]
    for label, done in steps:
        st.markdown(f"{'🟢' if done else '⚪'} {label}")
    st.divider()
    st.caption("CSV · Excel · Data profiling · Quality checks")

def set_notice(message):
    st.session_state["notice"] = message

def get_active_df():
    if st.session_state.labelled_df is not None:
        return st.session_state.labelled_df
    if st.session_state.processed_df is not None:
        return st.session_state.processed_df
    return st.session_state.source_df

def metric_card(label, value, note=""):
    st.metric(label, value, help=note or None)

def show_profile(df):
    profile = profile_dataset(df)
    a, b, c, d = st.columns(4)
    with a:
        metric_card("Rows", f"{profile['rows']:,}")
    with b:
        metric_card("Columns", f"{profile['columns']:,}")
    with c:
        metric_card("Missing cells", f"{profile['missing_cells']:,}")
    with d:
        metric_card("Duplicate rows", f"{profile['duplicate_rows']:,}")
    st.markdown("#### Column overview")
    st.dataframe(profile["column_profile"], use_container_width=True, hide_index=True)
    if profile["missing_by_column"].sum() > 0:
        st.markdown("#### Missing values by column")
        st.bar_chart(profile["missing_by_column"])

def upload_dataset():
    st.markdown("## Upload & explore")
    st.write("Bring in a CSV or Excel file to begin. Your original data remains unchanged.")
    uploaded = st.file_uploader("Choose a dataset", type=["csv", "xlsx", "xls"], key="dataset_uploader")
    if uploaded is not None:
        signature = hashlib.sha256(uploaded.getvalue()).hexdigest()
        if signature != st.session_state.file_signature:
            try:
                if uploaded.name.lower().endswith(".csv"):
                    try:
                        df = pd.read_csv(uploaded)
                    except UnicodeDecodeError:
                        uploaded.seek(0)
                        df = pd.read_csv(uploaded, encoding="latin-1")
                else:
                    df = pd.read_excel(uploaded)
                if df.empty or len(df.columns) == 0:
                    st.error("This file has no usable rows or columns.")
                    return
                if df.columns.astype(str).duplicated().any():
                    st.error("Duplicate column names were found. Rename them before continuing.")
                    return
                st.session_state.source_df = df
                st.session_state.processed_df = None
                st.session_state.labelled_df = None
                st.session_state.validation_result = None
                st.session_state.file_signature = signature
                st.session_state.source_name = uploaded.name
                st.session_state.history = [f"Uploaded {uploaded.name}"]
                st.success(f"Loaded {uploaded.name}")
            except Exception as exc:
                st.error(f"Could not read this file: {exc}")
                return
    if st.session_state.source_df is not None:
        st.markdown(f"### {st.session_state.source_name or 'Current dataset'}")
        show_profile(st.session_state.source_df)
        with st.expander("Preview and search source data", expanded=True):
            preview = st.session_state.source_df
            search = st.text_input("Search across rows", placeholder="Type a word or phrase...")
            if search.strip():
                mask = preview.astype(str).apply(lambda col: col.str.contains(search, case=False, regex=False, na=False)).any(axis=1)
                preview = preview.loc[mask]
            selected_columns = st.multiselect("Columns to display", list(preview.columns), default=list(preview.columns))
            st.caption(f"Showing {min(len(preview), 100):,} of {len(preview):,} matching rows")
            st.dataframe(preview[selected_columns].head(100), use_container_width=True, hide_index=True)
    else:
        st.info("Upload a file above, or try the included sample dataset.")
        if st.button("Load sample reviews", type="secondary"):
            sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "reviews.csv")
            st.session_state.source_df = pd.read_csv(sample_path)
            st.session_state.processed_df = None
            st.session_state.labelled_df = None
            st.session_state.validation_result = None
            st.session_state.file_signature = "sample-reviews"
            st.session_state.source_name = "reviews.csv"
            st.session_state.history = ["Loaded sample reviews"]
            st.rerun()

def preprocessing_page():
    st.markdown("## Preprocessing")
    source = st.session_state.source_df
    if source is None:
        st.info("Upload a dataset first.")
        return
    st.write("Choose how to handle missing values and duplicates before running the cleaning pipeline.")
    with st.form("preprocess_options"):
        remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
        drop_empty_rows = st.checkbox("Remove completely empty rows", value=True)
        trim_text = st.checkbox("Trim whitespace in text cells", value=True)
        normalize_columns = st.checkbox("Normalize column names", value=False)
        normalize_text = st.checkbox("Normalize text (collapse repeated spaces)", value=True)
        numeric_strategy = st.selectbox("Missing numeric values", ["Median", "Mean", "Zero", "Leave missing"])
        text_strategy = st.selectbox("Missing text values", ["Fill with Unknown", "Fill with empty text", "Leave missing"])
        run = st.form_submit_button("Run preprocessing", type="primary", use_container_width=True)
    if run:
        try:
            cleaned, report = preprocess_data(
                source,
                remove_duplicates=remove_duplicates,
                drop_empty_rows=drop_empty_rows,
                trim_text=trim_text,
                normalize_columns=normalize_columns,
                normalize_text=normalize_text,
                numeric_strategy=numeric_strategy,
                text_strategy=text_strategy,
                return_report=True,
            )
            st.session_state.processed_df = cleaned
            st.session_state.labelled_df = None
            st.session_state.validation_result = None
            st.session_state.history.append("Preprocessing completed")
            st.success("Preprocessing completed.")
            st.dataframe(pd.DataFrame([report]), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Preprocessing failed: {exc}")
    if st.session_state.processed_df is not None:
        st.markdown("### Processed data preview")
        st.dataframe(st.session_state.processed_df.head(200), use_container_width=True, hide_index=True)
        st.download_button(
            "Download processed CSV",
            st.session_state.processed_df.to_csv(index=False).encode("utf-8-sig"),
            "processed_dataset.csv",
            "text/csv",
        )

def labelling_page():
    st.markdown("## Labelling studio")
    st.caption("Create transparent labels from text keywords or numeric thresholds.")
    df = st.session_state.processed_df
    if df is None:
        df = st.session_state.source_df
        if df is not None:
            st.info("No processed dataset yet. You can label the original dataset or preprocess it first.")
    if df is None:
        st.info("Upload a dataset first.")
        return

    kind = st.radio(
        "Choose a labelling method",
        ["Text / keyword rules", "Numeric threshold rules"],
        horizontal=True,
        help="Numeric rules label rows by comparing a column to a value you choose.",
    )

    if kind == "Numeric threshold rules":
        st.markdown("### Numeric rule builder")
        st.write("Example: label records as **High Value** when `amount > 2000`, or choose any threshold and comparison operator.")
        numeric_candidates = [c for c in df.columns if pd.to_numeric(df[c], errors="coerce").notna().any()]
        if not numeric_candidates:
            st.warning("No numeric-compatible columns found. Upload a dataset with a numeric column or preprocess it first.")
            return
        with st.form("numeric_label_form"):
            c1, c2, c3 = st.columns([1.5, 1, 1])
            with c1:
                numeric_column = st.selectbox("Numeric column", numeric_candidates)
            with c2:
                numeric_operator = st.selectbox("Comparison", [">", ">=", "<", "<=", "==", "!="], index=0)
            with c3:
                numeric_threshold = st.number_input("Threshold value", value=2000.0, step=100.0, format="%.4f")
            st.markdown("#### Label names")
            c4, c5 = st.columns(2)
            with c4:
                true_label = st.text_input("When condition is TRUE", value="High Value")
            with c5:
                false_label = st.text_input("When condition is FALSE", value="Standard Value")
            missing_label = st.text_input("Missing / non-numeric values label", value="Missing / Invalid")
            numeric_submit = st.form_submit_button("Generate numeric labels", type="primary", use_container_width=True)
        if numeric_submit:
            try:
                labelled = add_numeric_labels(
                    df, numeric_column, numeric_operator, numeric_threshold,
                    true_label=true_label, false_label=false_label, missing_label=missing_label,
                )
                st.session_state.labelled_df = labelled
                st.session_state.validation_result = None
                st.session_state.history.append(f"Numeric labels applied: {numeric_column} {numeric_operator} {numeric_threshold:g}")
                st.success(f"Labels generated using `{numeric_column} {numeric_operator} {numeric_threshold:g}`.")
            except Exception as exc:
                st.error(f"Numeric labelling failed: {exc}")
        st.markdown("#### Rule preview")
        st.code(f"IF {numeric_column} {numeric_operator} {numeric_threshold:g} → {true_label if 'true_label' in locals() else 'High Value'}\nELSE → {false_label if 'false_label' in locals() else 'Standard Value'}\nMissing / invalid → separate label", language="text")
    else:
        with st.form("label_form"):
            column = st.selectbox("Text column", list(df.columns))
            mode = st.selectbox("Labelling mode", ["Keyword matching", "Multiple keyword rules"])
            positive_terms = st.text_input("Positive keyword(s)", value="great, excellent, love, good, amazing")
            negative_terms = st.text_input("Negative keyword(s)", value="bad, poor, hate, terrible, awful")
            neutral_label = st.checkbox("Use Neutral for rows matching neither side", value=True)
            case_sensitive = st.checkbox("Case-sensitive matching", value=False)
            submit = st.form_submit_button("Apply text labels", type="primary", use_container_width=True)
        if submit:
            try:
                labelled = add_labels(
                    df, column, positive_terms, negative_terms,
                    neutral_label=neutral_label, case_sensitive=case_sensitive,
                    mode=mode,
                )
                st.session_state.labelled_df = labelled
                st.session_state.validation_result = None
                st.session_state.history.append(f"Text labels applied to {column}")
                st.success("Labels applied. Review the distribution before exporting.")
            except Exception as exc:
                st.error(f"Labelling failed: {exc}")

    labelled = st.session_state.labelled_df
    if labelled is not None:
        st.markdown("### Label results")
        counts = labelled["Label"].value_counts(dropna=False)
        cols = st.columns(max(1, min(len(counts), 4)))
        for col, (label, count) in zip(cols, counts.items()):
            col.metric(str(label), f"{count:,}", f"{count / max(len(labelled), 1):.1%} of rows")
        left, right = st.columns([1, 2])
        with left:
            st.markdown("#### Label distribution")
            st.bar_chart(counts)
        with right:
            st.markdown("#### Labelled data preview")
            st.dataframe(labelled.head(200), use_container_width=True, hide_index=True)
        st.download_button(
            "Download labelled CSV",
            labelled.to_csv(index=False).encode("utf-8-sig"),
            "labelled_dataset.csv",
            "text/csv",
            use_container_width=True,
        )

def validation_page():
    st.markdown("## Data quality & validation")
    df = get_active_df()
    if df is None:
        st.info("Upload a dataset first.")
        return
    if st.button("Run validation checks", type="primary", use_container_width=True):
        st.session_state.validation_result = validate_dataset(df)
        st.session_state.history.append("Validation completed")
    result = st.session_state.validation_result
    if result is None:
        st.info("Run the checks to see a quality report.")
    else:
        if result["valid"]:
            st.success("All configured validation checks passed.")
        else:
            st.warning("Some checks need attention.")
        a, b = st.columns(2)
        a.metric("Checks passed", result["passed"])
        b.metric("Issues found", result["failed"])
        for item in result["checks"]:
            with st.container(border=True):
                st.markdown(f"{'✅' if item['passed'] else '⚠️'} **{item['name']}**")
                st.caption(item["message"])
        st.download_button(
            "Download validation report",
            report_to_text(result).encode("utf-8"),
            "validation_report.txt",
            "text/plain",
        )


def compare_versions_page():
    st.markdown("## Compare dataset versions")
    source = st.session_state.source_df
    current = get_active_df()
    if source is None or current is None:
        st.info("Upload a dataset first. Run preprocessing or labelling to create another version to compare.")
        return
    source_profile = profile_dataset(source)
    current_profile = profile_dataset(current)
    st.caption("Compare the original upload with the latest available version. The original dataset is kept unchanged.")
    a, b, c, d = st.columns(4)
    a.metric("Rows", f"{len(current):,}", f"{len(current) - len(source):+,} vs original")
    b.metric("Columns", f"{len(current.columns):,}", f"{len(current.columns) - len(source.columns):+,} vs original")
    a2 = source_profile["missing_cells"]
    b2 = current_profile["missing_cells"]
    c.metric("Missing cells", f"{b2:,}", f"{b2 - a2:+,} vs original", delta_color="inverse")
    c0 = source_profile["duplicate_rows"]
    d.metric("Duplicate rows", f"{current_profile['duplicate_rows']:,}", f"{current_profile['duplicate_rows'] - c0:+,} vs original", delta_color="inverse")
    st.markdown("### Version summary")
    comparison = pd.DataFrame([
        {"Metric": "Rows", "Original": len(source), "Current": len(current)},
        {"Metric": "Columns", "Original": len(source.columns), "Current": len(current.columns)},
        {"Metric": "Missing cells", "Original": a2, "Current": b2},
        {"Metric": "Duplicate rows", "Original": c0, "Current": current_profile["duplicate_rows"]},
    ])
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    added = [str(c) for c in current.columns if c not in source.columns]
    removed = [str(c) for c in source.columns if c not in current.columns]
    left, right = st.columns(2)
    with left:
        st.markdown("#### Added columns")
        st.write(", ".join(added) if added else "No added columns")
    with right:
        st.markdown("#### Removed columns")
        st.write(", ".join(removed) if removed else "No removed columns")
    if "Label" in current.columns:
        st.markdown("### Current label distribution")
        st.bar_chart(current["Label"].value_counts())

def export_page():
    st.markdown("## Export center")
    df = get_active_df()
    if df is None:
        st.info("Upload a dataset first.")
        return
    st.write("Export the latest available version. The labelled dataset is used when it exists.")
    st.markdown(f"**Exporting:** {len(df):,} rows × {len(df.columns):,} columns")
    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8-sig"),
            "dataset_export.csv",
            "text/csv",
            use_container_width=True,
        )
    with right:
        st.download_button(
            "Download Excel",
            dataframe_to_excel(df),
            "dataset_export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    if st.session_state.validation_result:
        st.download_button(
            "Download validation report",
            report_to_text(st.session_state.validation_result).encode("utf-8"),
            "validation_report.txt",
            "text/plain",
            use_container_width=True,
        )

def overview_page():
    st.markdown("# Dataset workspace")
    st.markdown("Prepare, label, and validate your data in one workflow.")
    st.markdown("")
    df = get_active_df()
    if df is None:
        a, b = st.columns([1.3, 1])
        with a:
            st.markdown("### Turn raw data into analysis-ready data")
            st.write("Upload CSV or Excel files, inspect data quality, clean missing values, apply transparent label rules, and export results.")
            if st.button("Start with a dataset", type="primary"):
                st.session_state["requested_page"] = "Upload & Explore"
                st.rerun()
        with b:
            st.markdown("#### Included capabilities")
            st.markdown("- Dataset profiling\n- Configurable preprocessing\n- Rule-based text labels\n- Validation report\n- CSV and Excel exports")
        return
    profile = profile_dataset(df)
    a, b, c, d = st.columns(4)
    with a:
        metric_card("Rows", f"{profile['rows']:,}")
    with b:
        metric_card("Columns", f"{profile['columns']:,}")
    with c:
        metric_card("Missing cells", f"{profile['missing_cells']:,}")
    with d:
        metric_card("Duplicate rows", f"{profile['duplicate_rows']:,}")
    st.markdown("### Dataset health")
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("#### Missing values by column")
        st.bar_chart(profile["missing_by_column"])
    with right:
        st.markdown("#### Label distribution")
        if "Label" in df.columns:
            st.bar_chart(df["Label"].value_counts())
        else:
            st.info("Apply labels to see the distribution here.")
        st.markdown("#### Recent activity")
        for event in reversed(st.session_state.history[-5:]):
            st.write(f"• {event}")
    st.markdown("### Quick actions")
    c1, c2, c3 = st.columns(3)
    if c1.button("Explore data", use_container_width=True):
        st.session_state["requested_page"] = "Upload & Explore"
        st.rerun()
    if c2.button("Preprocess", use_container_width=True):
        st.session_state["requested_page"] = "Preprocessing"
        st.rerun()
    if c3.button("Validate", use_container_width=True):
        st.session_state["requested_page"] = "Validation"
        st.rerun()

requested_page = st.session_state.pop("requested_page", None)
if requested_page:
    page = requested_page

if page == "Overview":
    overview_page()
elif page == "Upload & Explore":
    upload_dataset()
elif page == "Preprocessing":
    preprocessing_page()
elif page == "Labelling":
    labelling_page()
elif page == "Validation":
    validation_page()
elif page == "Compare Versions":
    compare_versions_page()
elif page == "Export":
    export_page()
