
class DataHealthReport:
    def __init__(
        self,
        health_score: int,
        shape: dict,
        column_types: dict,
        missing_percentage: dict,
        duplicate_rows: int,
        warnings: dict,
        recommendations : dict,
        numeric: dict,
    ):
        self.health_score = health_score
        self.shape = shape
        self.column_types = column_types
        self.missing_percentage = missing_percentage
        self.duplicate_rows = duplicate_rows
        self.warnings = warnings
        self.recommendations = recommendations
        self.numeric = numeric

    def summary(self) -> None:
        print(f"Data Health Score: {self.health_score}/100")
        print(f"Rows: {self.shape['rows']} | No_Columns: {self.shape['columns']}")
        print()
        print(f"Numeric Columns : {self.column_types['numeric']}")
        print(f"Categorical Columns : {self.column_types['categorical']}")
        print(f"DateTime Columns : {self.column_types['datetime']}")
        print()
        print(f"Missing Percentage: ")
        for col in self.missing_percentage:
            if self.missing_percentage[col] > 0:
                print(f"- {col}: {self.missing_percentage[col]}%")

        if self.warnings:
            print("\nWarnings:")
            for k, v in self.warnings.items():
                if v:
                    print(f"- {k}: {v}")
        else:
            print("\nNo major data issues detected")

        print("\nRecommendations:")
        for k, v in self.recommendations.items():
            print(f"- {k}: {v}")

        print("\nNumeric Diagnostics:")
        for col, info in self.numeric.items():
            print(
                f"- {col}: skew={info['skewness']}, "
                f"outliers={info['outlier_percentage']}%, "
                f"{info['recommendation']}"
            )

    def to_dict(self) -> dict:
        return {
            "health_score": self.health_score,
            "shape": self.shape,
            "column_types": self.column_types,
            "missing_percentage": self.missing_percentage,
            "duplicate_rows": self.duplicate_rows,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "Numeric Diagnostics": self.numeric
        }

    def to_json(self, path: str | None = None) -> dict:
        import json

        data = {
            "health_score": self.health_score,
            "shape": self.shape,
            "column_types": self.column_types,
            "missing_percentage": self.missing_percentage,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "numeric_diagnostics": self.numeric
        }

        if path:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)

        return data


    def to_markdown(self, path: str | None = None) -> str:
        lines = []

        # Title
        lines.append("# Data Health Report\n")

        # Summary
        lines.append("## Summary")
        lines.append(f"- **Health Score:** {self.health_score}/100")
        lines.append(f"- **Rows:** {self.shape['rows']}")
        lines.append(f"- **Columns:** {self.shape['columns']}\n")

        # Column Types
        lines.append("## Column Types")
        for k, v in self.column_types.items():
            lines.append(f"- **{k.capitalize()}**: {v}")
        lines.append("")

        # Missing Percentage
        lines.append("## Missing Percentage")
        for col, pct in self.missing_percentage.items():
            if pct > 0:
                lines.append(f"- **{col}**: {pct}%")
        lines.append("")

        # Warnings
        lines.append("## Warnings")
        if any(self.warnings.values()):
            for k, v in self.warnings.items():
                lines.append(f"- **{k}**: {v}")
        else:
            lines.append("- No major warnings")
        lines.append("")

        # Recommendations
        lines.append("## Recommendations")

        # Encoding
        if "encoding" in self.recommendations:
            lines.append("### Encoding")
            for col, info in self.recommendations["encoding"].items():
                lines.append(
                    f"- **{col}**: {info['message']} "
                    f"(Confidence: {info['confidence']})"
                )

        # Missing
        if "missing" in self.recommendations:
            lines.append("\n### Missing Values")
            for col, info in self.recommendations["missing"].items():
                lines.append(
                    f"- **{col}**: {info['action']} "
                    f"({info['message']}, Confidence: {info['confidence']})"
                )
        lines.append("")

        # Numeric Diagnostics
        lines.append("## Numeric Diagnostics")
        for col, info in self.numeric.items():
            lines.append(
                f"- **{col}**: skew={info['skewness']}, "
                f"outliers={info['outlier_percentage']}%, "
                f"{info['recommendation']}"
            )

        markdown_text = "\n".join(lines)

        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(markdown_text)

        return markdown_text




