from sklearn.base import BaseEstimator, TransformerMixin
from yreport import data_health_report


class YReportInspector(BaseEstimator, TransformerMixin):
    """
    A sklearn-compatible inspector that generates a yreport
    during fit and passes data unchanged through the pipeline.
    """

    def __init__(
        self,
        drop_cols=None,
        categorical_cols=None,
        numerical_cols=None,
        ignore_cols=None
    ):
        self.drop_cols = drop_cols
        self.categorical_cols = categorical_cols
        self.ignore_cols = ignore_cols
        self.numerical_cols = numerical_cols

    def fit(self, X, y=None):
        # Generate and store report
        self.report_ = data_health_report(
            X,
            drop_cols=self.drop_cols,
            categorical_cols=self.categorical_cols,
            numeric_cols=self.numerical_cols,
            ignore_cols=self.ignore_cols
        )
        return self

    def transform(self, X):
        # IMPORTANT: do nothing to X
        return X
