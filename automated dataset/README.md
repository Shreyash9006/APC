# Automated Dataset Studio

A Streamlit app for exploring, cleaning, keyword-labelling, validating, and exporting CSV/Excel datasets.

## Features
- Dark responsive dashboard with workflow navigation
- CSV, XLSX, and XLS upload
- Dataset profiling: row/column counts, missing values, duplicates, unique counts, and dtypes
- Configurable preprocessing with before/after report
- Explainable positive/negative/neutral/mixed keyword labels
- Validation checks and downloadable text report
- CSV and Excel export
- Sample review dataset included

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Activate it:
- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
automated database/
├── app.py
├── assets/style.css
├── data/raw/check.csv
├── modules/
│   ├── __init__.py
│   ├── exporting.py
│   ├── labelling.py
│   ├── preprocessing.py
│   ├── profiling.py
│   └── validation.py
├── sample_data/reviews.csv
├── tests/
└── requirements.txt
```

## Labelling notes
Labelling is rule-based, not an ML model. Add comma-separated positive and negative terms. Rows matching both become `Mixed`; unmatched rows become `Neutral` when that option is enabled. Review results before using them for decisions.

## Tests
Run `pytest -q`.


## Advanced features

- Search rows and choose columns in the dataset preview.
- Compare the original dataset with the latest processed/labelled version.
- Configure text normalization, whitespace trimming, missing-value handling, duplicate removal, and optional column-name normalization.
- Inspect validation reports and export CSV, Excel, and validation text reports.
- Original uploaded data is kept separately from processed results.
