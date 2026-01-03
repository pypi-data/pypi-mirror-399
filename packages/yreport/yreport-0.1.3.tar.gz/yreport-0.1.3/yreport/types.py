import pandas as pd


def detect_column_types(df: pd.DataFrame) -> dict:
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(include="object").columns.tolist()
    datetime = df.select_dtypes(include="datetime").columns.tolist()

    return {
        "numeric": numeric,
        "categorical": categorical,
        "datetime": datetime
    }
