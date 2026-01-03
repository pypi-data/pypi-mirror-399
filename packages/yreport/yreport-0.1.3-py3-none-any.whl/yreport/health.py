# yreport/health.py
import pandas as pd
from .types import detect_column_types
from .report import DataHealthReport
from .recommend import generate_recommendations
from .recommend import numeric_diagnostics

WEIGHTS = {
    "missing": 0.5,
    "duplicates": 0.3,
    "cardinality": 0.2
}

def data_health_report(df: pd.DataFrame, drop_cols=None,
    categorical_cols=None,
    numeric_cols=None,
    ignore_cols=None) -> DataHealthReport:

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    drop_cols = set(drop_cols or [])
    categorical_cols = set(categorical_cols or [])
    numeric_cols = set(numeric_cols or [])
    ignore_cols = set(ignore_cols or [])

    # ignore cols
    df = df.drop(columns=ignore_cols, errors="ignore")

    # categorical vs numerical

    column_types = detect_column_types(df)
    # convert to sets for safe manipulation
    column_types["numeric"] = set(column_types["numeric"])
    column_types["categorical"] = set(column_types["categorical"])
    column_types["datetime"] = set(column_types["datetime"])

    # Apply user overrides
    if categorical_cols:
        column_types["categorical"].update(categorical_cols)
        column_types["numeric"].difference_update(categorical_cols)

    if numeric_cols:
        column_types["numeric"].update(numeric_cols)
        column_types["categorical"].difference_update(numeric_cols)

    # Remove ignored columns from ALL types
    for key in column_types:
        column_types[key].difference_update(ignore_cols)

    # Convert back to lists
    for key in column_types:
        column_types[key] = sorted(column_types[key])

    #rows , cols
    rows, cols = df.shape
    #column_types = detect_column_types(df)

    # Missing
    missing_ratio = df.isnull().mean().mean()
    missing_score = 1 - missing_ratio

    # Duplicates
    duplicate_ratio = df.duplicated().mean()
    duplicate_score = 1 - duplicate_ratio

    # recommendation
    recommendations = generate_recommendations(df,drop_cols ,column_types)
    numeric = numeric_diagnostics(df, column_types['numeric'])

    # Cardinality
    drop_cols = {
        col for col, info in recommendations["missing"].items()
        if info["action"] == "drop"
    }
    categorical_cols = column_types["categorical"]
    high_card_cols = [
        col for col in column_types["categorical"]
        if df[col].nunique() > 50 and col not in drop_cols
    ]

    cardinality_ratio = (
        len(high_card_cols) / max(len(categorical_cols), 1)
    )
    cardinality_score = 1 - cardinality_ratio

    # Final Weighted Score
    final_score = (
        missing_score * WEIGHTS["missing"] +
        duplicate_score * WEIGHTS["duplicates"] +
        cardinality_score * WEIGHTS["cardinality"]
    ) * 100


    return DataHealthReport(
        health_score=round(final_score, 2),
        shape={"rows": rows, "columns": cols},
        column_types=column_types,
        missing_percentage=(df.isnull().mean() * 100).round(2).to_dict(),
        duplicate_rows=int(df.duplicated().sum()),
        warnings={
            "high_missing": [
                col for col, pct in (df.isnull().mean() * 100).items()
                if pct > 30
            ],
            "high_cardinality": high_card_cols

        },
         recommendations = recommendations,
        numeric = numeric
    )
