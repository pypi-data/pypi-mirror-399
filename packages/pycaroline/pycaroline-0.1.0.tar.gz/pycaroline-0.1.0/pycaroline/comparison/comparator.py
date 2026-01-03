"""DataComparator class for comparing DataFrames using datacompy with Polars."""

import polars as pl
from datacompy.polars import PolarsCompare

from pycaroline.comparison.models import ComparisonConfig, ComparisonResult


class DataComparator:
    """Compares two Polars DataFrames using datacompy.

    This class wraps datacompy.PolarsCompare with preprocessing options for
    whitespace stripping and case normalization.

    Attributes:
        config: ComparisonConfig instance with comparison settings.
    """

    def __init__(self, config: ComparisonConfig):
        """Initialize the comparator with configuration.

        Args:
            config: ComparisonConfig instance specifying join columns,
                   tolerances, and preprocessing options.
        """
        self.config = config

    def compare(
        self,
        source_df: pl.DataFrame,
        target_df: pl.DataFrame,
        source_name: str = "source",
        target_name: str = "target",
    ) -> ComparisonResult:
        """Compare two Polars DataFrames and return results.

        Args:
            source_df: Source DataFrame to compare.
            target_df: Target DataFrame to compare.
            source_name: Name for the source DataFrame in reports.
            target_name: Name for the target DataFrame in reports.

        Returns:
            ComparisonResult containing all comparison outputs.
        """
        # Clone to avoid modifying original DataFrames
        source_df = source_df.clone()
        target_df = target_df.clone()

        # Run comparison using datacompy PolarsCompare
        compare = PolarsCompare(
            source_df,
            target_df,
            join_columns=self.config.join_columns,
            abs_tol=self.config.abs_tol,
            rel_tol=self.config.rel_tol,
            df1_name=source_name,
            df2_name=target_name,
            ignore_spaces=self.config.ignore_spaces,
            ignore_case=self.config.ignore_case,
            cast_column_names_lower=False,
        )

        # Get mismatched rows
        try:
            mismatched = compare.all_mismatch()
        except Exception:
            # If no mismatches or error, return empty DataFrame
            mismatched = pl.DataFrame()

        # Build column stats DataFrame
        column_stats = self._build_column_stats(compare)

        return ComparisonResult(
            source_row_count=len(source_df),
            target_row_count=len(target_df),
            matching_rows=compare.count_matching_rows(),
            mismatched_rows=len(mismatched),
            rows_only_in_source=compare.df1_unq_rows,
            rows_only_in_target=compare.df2_unq_rows,
            mismatched_columns=mismatched,
            column_stats=column_stats,
            report_text=compare.report(),
        )

    def _build_column_stats(self, compare: PolarsCompare) -> pl.DataFrame:
        """Build column statistics DataFrame from comparison.

        Args:
            compare: datacompy.PolarsCompare instance.

        Returns:
            Polars DataFrame with column-level statistics.
        """
        stats_data = []

        # Get all columns from both DataFrames
        all_columns = set(compare.df1.columns) | set(compare.df2.columns)

        for col in all_columns:
            in_source = col in compare.df1.columns
            in_target = col in compare.df2.columns

            col_stat = {
                "column": col,
                "in_source": in_source,
                "in_target": in_target,
                "source_dtype": str(compare.df1[col].dtype) if in_source else None,
                "target_dtype": str(compare.df2[col].dtype) if in_target else None,
            }

            # Add match statistics if column is in both
            if in_source and in_target and col not in self.config.join_columns:
                # Check if column has comparison stats
                if hasattr(compare, "column_stats") and compare.column_stats:
                    for stat in compare.column_stats:
                        if stat.get("column") == col:
                            col_stat["match_count"] = stat.get("match_cnt", 0)
                            col_stat["mismatch_count"] = stat.get("unequal_cnt", 0)
                            break

            stats_data.append(col_stat)

        return pl.DataFrame(stats_data)
