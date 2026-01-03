# yreport/recommend.py
import pandas as pd
import numpy as np
from scipy.stats import skew


def generate_recommendations(df: pd.DataFrame,drop_cols ,column_types: dict) -> dict:
    recommendations = {
        "encoding": {},
        "missing": {}
    }

    missing_pct = (df.isnull().mean() * 100).round(2).to_dict()

    # ---- Missing value rules ----
    for col in missing_pct:
        if missing_pct[col] > 60:
            recommendations["missing"][col] = {
                "action": "drop",
                "message": f"{missing_pct[col]}% missing values",
                "confidence": "HIGH"
            }
        elif missing_pct[col] > 5:
            recommendations["missing"][col] = {
                "action": "impute",
                "message": f"{missing_pct[col]}% missing values",
                "confidence": "MEDIUM"
        }

    drop_cols = drop_cols | { col for col, info in recommendations["missing"].items()
        if info["action"] == "drop"}

    # Force user-defined drop columns
    for col in drop_cols:
        recommendations["missing"][col] = {
            "action": "drop",
            "message": "Dropped by user configuration",
            "confidence": "HIGH"
        }

    # ---- Encoding (categorical) ----

    for col in column_types["categorical"]:
        if col in drop_cols:
            continue

        high_card = df[col].nunique() > 50

        recommendations["encoding"][col] = {
            "action": 'required',
            "message": (
                "Categorical encoding required (high cardinality)"
                if high_card else
                "Categorical encoding required"
            ),
            "confidence": "HIGH" if high_card else "MEDIUM"
        }
    return recommendations

# numeric diagnostics

def numeric_diagnostics(df, numeric_cols):
    diagnostics = {}

    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        col_skew = skew(series)

        q1, q3 = np.percentile(series, [25, 75])
        iqr = q3 - q1
        outlier_mask = (series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)
        outlier_pct = outlier_mask.mean() * 100

        diagnostics[col] = {
            "skewness": round(col_skew, 2),
            "outlier_percentage": round(outlier_pct, 2),
            "recommendation": (
                "consider log/robust transform"
                if abs(col_skew) > 1 or outlier_pct > 5
                else "no transform needed"
            ),
            "confidence": "HIGH" if abs(col_skew) > 1 else "MEDIUM"
        }

    return diagnostics
