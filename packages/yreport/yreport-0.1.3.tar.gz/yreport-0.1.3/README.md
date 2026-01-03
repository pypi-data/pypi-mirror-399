# 📊 yreport
<img src="https://img.shields.io/github/actions/workflow/status/Yogesh942134/yreport/release.yml">

<p align="center">
  <a href="https://pypi.org/project/yreport/">
    <img src="https://img.shields.io/pypi/v/yreport.svg">
  </a>
  <a href="https://pypi.org/project/yreport/">
    <img src="https://img.shields.io/pypi/pyversions/yreport.svg">
  </a>
  <img src="https://img.shields.io/github/license/Yogesh942134/yreport">
</p>

## 📦 Install

```bash
pip install yreport
```
**yreport** is a lightweight, dataset-agnostic **data health reporting library** for tabular datasets.  
It analyzes data quality, detects potential issues, and provides **honest, actionable diagnostics** without making unsafe assumptions.

Unlike heavy EDA tools, `yreport` is designed to be:
- Pipeline-friendly
- Explainable
- Configurable
- Production-aware

---

## 🚀 Why yreport?

Most EDA libraries:
- Generate large HTML reports
- Make aggressive assumptions (e.g. one-hot everything)
- Are hard to integrate into ML pipelines

**yreport focuses on decisions, not decoration.**

It helps answer:
- Is this dataset usable?
- Which columns are problematic?
- What should be fixed first?
- Where should I be careful before modeling?

---

## ✨ Features

- Weighted **Data Health Score (0–100)**
- Automatic column type detection
- Missing value diagnostics with confidence levels
- High-cardinality categorical detection
- Numeric skewness and outlier analysis
- Honest categorical handling (no forced one-hot / ordinal)
- User override support
- Non-contradictory recommendations
- JSON and Markdown export
- scikit-learn Pipeline integration
- Lightweight and fast

---

## 📦 Installation

### Install from source (recommended)

```bash
git clone https://github.com/Yogesh942134/yreport.git
cd yreport
pip install -e .
```

### 🧠 Core Concept

yreport does not modify your data.

It:
- Inspects datasets
- Reports potential issues
- Suggests actions with confidence

It does not:
- Apply transformations
- Guess encoding methods
- Perform feature engineering
- This makes it safe and transparent.
  
```bash
import pandas as pd
from yreport import data_health_report

df = pd.read_csv("data.csv")

report = data_health_report(df)
report.summary()
```

Example Console Output:
Data Health Score: 87.95/100
Rows: 891 | No_Columns: 12

Warnings:
- high_missing: ['Cabin']
- high_cardinality: ['Name', 'Ticket']

### 📋 What the Report Includes

1️⃣ Data Health Score
A weighted score based on:
- Missing values
- Duplicate rows
- High-cardinality features

2️⃣ Column Type Detection
Automatically detects:
- Numeric columns
- Categorical columns
- Datetime columns

3️⃣ Missing Value Diagnostics
- Missing percentage per column
- Drop or impute recommendations
- Confidence levels: HIGH / MEDIUM

4️⃣ Categorical Diagnostics
- Flags categorical columns that require encoding
- Detects high-cardinality features
- Does not assume one-hot or ordinal encoding

5️⃣ Numeric Diagnostics
For numeric columns:
- Skewness
- Outlier percentage (IQR method)
- Transform suggestions (log / robust)

### 🧩 User Overrides

Automatic detection is never perfect.
yreport allows explicit user control.

Supported Overrides:
```bash
data_health_report(
    df,
    ignore_cols=[...],
    drop_cols=[...],
    categorical_cols=[...],
    numerical_cols=[...]
)
```
Meaning of Overides:
| Override           | Purpose                     |
| ------------------ | --------------------------- |
| `ignore_cols`      | Completely ignore columns   |
| `drop_cols`        | Force drop columns          |
| `categorical_cols` | Force categorical treatment |
| `numerical_cols`   | Force numeric treatment     |

Rules:
- User intent always overrides automation
- A column belongs to only one semantic type
- Ignored or dropped columns are excluded everywhere

### 📤 Exporting Reports
JSON Export (machine-readable):
```bash
report.to_json("report.json")/data = report.to_json()
```

Markdown Export (human-readable)
```bash
report.to_markdown("report.md")
```
### 🤖 scikit-learn Pipeline Integration

yreport provides a no-op sklearn inspector.
Why?
- Observe data during training
- Do not interfere with models
- Keep pipelines clean

Example
```bash
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from yreport import YReportInspector

pipe = Pipeline([
    ("inspect", YReportInspector(
        categorical_cols=["Pclass"],
        ignore_cols=["Name"]
    )),
    ("model", LogisticRegression(max_iter=1000))
])

pipe.fit(X_train, y_train)

pipe.named_steps["inspect"].report_.summary()
pipe.named_steps["inspect"].report_.to_markdown("train_report.md")
```
✔ Model trains normally
✔ Data remains unchanged
✔ Report is available after fit()

### 🧪 Testing

Run tests from the project root:
```bash
pytest
```
Includes:
- sklearn pipeline compatibility test
- Core API regression protection

### 🧠 Design Philosophy

- Correctness > Automation
- Transparency > Guessing
- Diagnostics > Decoration
- User intent > Heuristics

yreport will never silently apply transformations.

### 🚧 What yreport is NOT

- AutoML tool
- Feature engineering pipeline
- Visualization-heavy EDA
- Encoding decision engine

This is intentional.

