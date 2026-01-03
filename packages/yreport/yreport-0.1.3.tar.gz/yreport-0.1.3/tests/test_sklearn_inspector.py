def test_yreport_inspector_pipeline():
    import pandas as pd
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LogisticRegression
    from yreport import YReportInspector
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer

    # Dummy dataset
    X = pd.DataFrame({
        "num": [1, 2, 3, 4],
        "cat": ["a", "b", "a", "b"]
    })
    y = [0, 1, 0, 1]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(), ["cat"]),
            ("num", "passthrough", ["num"])
        ]
    )

    pipe = Pipeline([
        ("inspect", YReportInspector(categorical_cols=['cat'])),
        ('preprocessor', preprocessor),
        ("model", LogisticRegression())
    ])

    # Should fit without error
    pipe.fit(X, y)

    # Inspector must store report_
    inspector = pipe.named_steps["inspect"]
    assert hasattr(inspector, "report_")

    # Model must still predict
    preds = pipe.predict(X)
    assert len(preds) == len(X)
