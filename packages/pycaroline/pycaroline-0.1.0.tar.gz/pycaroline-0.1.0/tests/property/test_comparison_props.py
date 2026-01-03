"""Property-based tests for data comparison.

These tests validate universal properties of the DataComparator using hypothesis.
"""

import polars as pl
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from pycaroline.comparison.comparator import DataComparator
from pycaroline.comparison.models import ComparisonConfig


class TestProperty7SourceOnlyRowsDetection:
    """
    **Feature: data-validation-library, Property 7: Source-Only Rows Detection**
    **Validates: Requirements 3.2**

    For any two DataFrames where source contains rows with keys not present
    in target, rows_only_in_source SHALL contain exactly those rows.
    """

    @given(
        source_ids=st.lists(
            st.integers(min_value=1, max_value=1000),
            min_size=1,
            max_size=20,
            unique=True,
        ),
        target_ids=st.lists(
            st.integers(min_value=1, max_value=1000),
            min_size=0,
            max_size=20,
            unique=True,
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_source_only_rows_detected(self, source_ids: list, target_ids: list):
        """
        **Feature: data-validation-library, Property 7: Source-Only Rows Detection**
        **Validates: Requirements 3.2**

        For any source and target with different ID sets, rows only in source
        must be correctly identified.
        """
        # Create source DataFrame
        source_df = pl.DataFrame(
            {"id": source_ids, "value": [f"source_{i}" for i in source_ids]}
        )

        # Create target DataFrame
        if target_ids:
            target_df = pl.DataFrame(
                {"id": target_ids, "value": [f"target_{i}" for i in target_ids]}
            )
        else:
            target_df = pl.DataFrame({"id": [], "value": []}).cast(
                {"id": pl.Int64, "value": pl.Utf8}
            )

        # Calculate expected source-only IDs
        source_id_set = set(source_ids)
        target_id_set = set(target_ids)
        expected_only_in_source = source_id_set - target_id_set

        # Run comparison
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # Verify source-only rows
        actual_only_in_source = set(result.rows_only_in_source["id"].to_list())

        assert actual_only_in_source == expected_only_in_source, (
            f"Expected source-only IDs {expected_only_in_source}, "
            f"got {actual_only_in_source}"
        )


class TestProperty8TargetOnlyRowsDetection:
    """
    **Feature: data-validation-library, Property 8: Target-Only Rows Detection**
    **Validates: Requirements 3.3**

    For any two DataFrames where target contains rows with keys not present
    in source, rows_only_in_target SHALL contain exactly those rows.
    """

    @given(
        source_ids=st.lists(
            st.integers(min_value=1, max_value=1000),
            min_size=0,
            max_size=20,
            unique=True,
        ),
        target_ids=st.lists(
            st.integers(min_value=1, max_value=1000),
            min_size=1,
            max_size=20,
            unique=True,
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_target_only_rows_detected(self, source_ids: list, target_ids: list):
        """
        **Feature: data-validation-library, Property 8: Target-Only Rows Detection**
        **Validates: Requirements 3.3**

        For any source and target with different ID sets, rows only in target
        must be correctly identified.
        """
        # Create source DataFrame
        if source_ids:
            source_df = pl.DataFrame(
                {"id": source_ids, "value": [f"source_{i}" for i in source_ids]}
            )
        else:
            source_df = pl.DataFrame({"id": [], "value": []}).cast(
                {"id": pl.Int64, "value": pl.Utf8}
            )

        # Create target DataFrame
        target_df = pl.DataFrame(
            {"id": target_ids, "value": [f"target_{i}" for i in target_ids]}
        )

        # Calculate expected target-only IDs
        source_id_set = set(source_ids)
        target_id_set = set(target_ids)
        expected_only_in_target = target_id_set - source_id_set

        # Run comparison
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # Verify target-only rows
        actual_only_in_target = set(result.rows_only_in_target["id"].to_list())

        assert actual_only_in_target == expected_only_in_target, (
            f"Expected target-only IDs {expected_only_in_target}, "
            f"got {actual_only_in_target}"
        )


class TestProperty9MismatchedValuesDetection:
    """
    **Feature: data-validation-library, Property 9: Mismatched Values Detection**
    **Validates: Requirements 3.4**

    For any two DataFrames with rows having matching keys but differing
    non-key column values, mismatched_columns SHALL contain those rows.
    """

    @given(
        common_ids=st.lists(
            st.integers(min_value=1, max_value=1000),
            min_size=1,
            max_size=10,
            unique=True,
        ),
        mismatch_indices=st.lists(
            st.integers(min_value=0, max_value=9), min_size=0, max_size=5, unique=True
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_mismatched_values_detected(self, common_ids: list, mismatch_indices: list):
        """
        **Feature: data-validation-library, Property 9: Mismatched Values Detection**
        **Validates: Requirements 3.4**

        For any rows with matching keys but different values, the mismatches
        must be correctly identified.
        """
        # Filter mismatch_indices to valid range
        valid_mismatch_indices = [i for i in mismatch_indices if i < len(common_ids)]

        # Create source DataFrame
        source_df = pl.DataFrame(
            {"id": common_ids, "value": [f"value_{i}" for i in common_ids]}
        )

        # Create target DataFrame with some mismatched values
        target_values = [f"value_{i}" for i in common_ids]
        for idx in valid_mismatch_indices:
            target_values[idx] = f"different_{common_ids[idx]}"

        target_df = pl.DataFrame({"id": common_ids, "value": target_values})

        # Run comparison
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # Expected mismatched IDs
        expected_mismatched_ids = {common_ids[i] for i in valid_mismatch_indices}

        # Get actual mismatched IDs from result
        if len(result.mismatched_columns) > 0:
            actual_mismatched_ids = set(result.mismatched_columns["id"].to_list())
        else:
            actual_mismatched_ids = set()

        assert actual_mismatched_ids == expected_mismatched_ids, (
            f"Expected mismatched IDs {expected_mismatched_ids}, "
            f"got {actual_mismatched_ids}"
        )


class TestProperty10NumericToleranceHandling:
    """
    **Feature: data-validation-library, Property 10: Numeric Tolerance Handling**
    **Validates: Requirements 3.6**

    For any two numeric values where |a - b| <= abs_tol, the comparison
    SHALL consider them equal when tolerance is configured.
    """

    @given(
        base_values=st.lists(
            st.floats(
                min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False
            ),
            min_size=1,
            max_size=10,
        ),
        tolerance=st.floats(
            min_value=0.0001, max_value=1.0, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_values_within_tolerance_match(self, base_values: list, tolerance: float):
        """
        **Feature: data-validation-library, Property 10: Numeric Tolerance Handling**
        **Validates: Requirements 3.6**

        For any numeric values where the difference is within tolerance,
        they should be considered equal.
        """
        ids = list(range(len(base_values)))

        # Create source DataFrame
        source_df = pl.DataFrame({"id": ids, "amount": base_values})

        # Create target DataFrame with values within tolerance
        # Add half the tolerance to each value (guaranteed to be within tolerance)
        target_values = [v + (tolerance / 2) for v in base_values]
        target_df = pl.DataFrame({"id": ids, "amount": target_values})

        # Run comparison with tolerance
        config = ComparisonConfig(join_columns=["id"], abs_tol=tolerance)
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # All rows should match (no mismatches) since differences are within tolerance
        assert result.mismatched_rows == 0, (
            f"Expected 0 mismatched rows with tolerance {tolerance}, "
            f"got {result.mismatched_rows}"
        )
        assert result.matching_rows == len(
            base_values
        ), f"Expected {len(base_values)} matching rows, got {result.matching_rows}"

    @given(
        base_values=st.lists(
            st.floats(
                min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False
            ),
            min_size=1,
            max_size=10,
        ),
        tolerance=st.floats(
            min_value=0.0001, max_value=0.1, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_values_outside_tolerance_mismatch(
        self, base_values: list, tolerance: float
    ):
        """
        **Feature: data-validation-library, Property 10: Numeric Tolerance Handling**
        **Validates: Requirements 3.6**

        For any numeric values where the difference exceeds tolerance,
        they should be considered different.
        """
        ids = list(range(len(base_values)))

        # Create source DataFrame
        source_df = pl.DataFrame({"id": ids, "amount": base_values})

        # Create target DataFrame with values outside tolerance
        # Add twice the tolerance to each value (guaranteed to exceed tolerance)
        target_values = [v + (tolerance * 2) for v in base_values]
        target_df = pl.DataFrame({"id": ids, "amount": target_values})

        # Run comparison with tolerance
        config = ComparisonConfig(join_columns=["id"], abs_tol=tolerance)
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # All rows should be mismatched since differences exceed tolerance
        assert result.mismatched_rows == len(base_values), (
            f"Expected {len(base_values)} mismatched rows with tolerance {tolerance}, "
            f"got {result.mismatched_rows}"
        )


class TestProperty11CaseInsensitiveStringComparison:
    """
    **Feature: data-validation-library, Property 11: Case-Insensitive String Comparison**
    **Validates: Requirements 3.7**

    For any two string values that differ only in case, the comparison
    SHALL consider them equal when ignore_case=True.
    """

    @given(
        strings=st.lists(
            st.text(
                alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                min_size=1,
                max_size=20,
            ),
            min_size=1,
            max_size=10,
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_case_differences_ignored_when_enabled(self, strings: list):
        """
        **Feature: data-validation-library, Property 11: Case-Insensitive String Comparison**
        **Validates: Requirements 3.7**

        For any strings that differ only in case, they should match
        when ignore_case is True.
        """
        ids = list(range(len(strings)))

        # Create source DataFrame with original case
        source_df = pl.DataFrame({"id": ids, "name": strings})

        # Create target DataFrame with swapped case
        target_strings = [s.swapcase() for s in strings]
        target_df = pl.DataFrame({"id": ids, "name": target_strings})

        # Run comparison with ignore_case=True
        config = ComparisonConfig(join_columns=["id"], ignore_case=True)
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # All rows should match since case is ignored
        assert result.mismatched_rows == 0, (
            f"Expected 0 mismatched rows with ignore_case=True, "
            f"got {result.mismatched_rows}"
        )
        assert result.matching_rows == len(
            strings
        ), f"Expected {len(strings)} matching rows, got {result.matching_rows}"

    @given(
        strings=st.lists(
            st.text(
                alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                min_size=1,
                max_size=20,
            ),
            min_size=1,
            max_size=10,
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_case_differences_detected_when_disabled(self, strings: list):
        """
        **Feature: data-validation-library, Property 11: Case-Insensitive String Comparison**
        **Validates: Requirements 3.7**

        For any strings that differ in case, they should NOT match
        when ignore_case is False.
        """
        # Filter out strings that are case-insensitive (same when swapped)
        strings = [s for s in strings if s != s.swapcase()]
        assume(len(strings) > 0)

        ids = list(range(len(strings)))

        # Create source DataFrame with original case
        source_df = pl.DataFrame({"id": ids, "name": strings})

        # Create target DataFrame with swapped case
        target_strings = [s.swapcase() for s in strings]
        target_df = pl.DataFrame({"id": ids, "name": target_strings})

        # Run comparison with ignore_case=False (default)
        config = ComparisonConfig(join_columns=["id"], ignore_case=False)
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # All rows should be mismatched since case matters
        assert result.mismatched_rows == len(strings), (
            f"Expected {len(strings)} mismatched rows with ignore_case=False, "
            f"got {result.mismatched_rows}"
        )


class TestProperty12WhitespaceInsensitiveStringComparison:
    """
    **Feature: data-validation-library, Property 12: Whitespace-Insensitive String Comparison**
    **Validates: Requirements 3.8**

    For any two string values that differ only in leading/trailing whitespace,
    the comparison SHALL consider them equal when ignore_spaces=True.
    """

    @given(
        strings=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("L", "N")),
                min_size=1,
                max_size=20,
            ),
            min_size=1,
            max_size=10,
        ),
        leading_spaces=st.lists(
            st.integers(min_value=0, max_value=5), min_size=1, max_size=10
        ),
        trailing_spaces=st.lists(
            st.integers(min_value=0, max_value=5), min_size=1, max_size=10
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_whitespace_differences_ignored_when_enabled(
        self, strings: list, leading_spaces: list, trailing_spaces: list
    ):
        """
        **Feature: data-validation-library, Property 12: Whitespace-Insensitive String Comparison**
        **Validates: Requirements 3.8**

        For any strings that differ only in leading/trailing whitespace,
        they should match when ignore_spaces is True.
        """
        # Ensure lists are same length
        min_len = min(len(strings), len(leading_spaces), len(trailing_spaces))
        strings = strings[:min_len]
        leading_spaces = leading_spaces[:min_len]
        trailing_spaces = trailing_spaces[:min_len]

        ids = list(range(len(strings)))

        # Create source DataFrame with original strings
        source_df = pl.DataFrame({"id": ids, "name": strings})

        # Create target DataFrame with whitespace added
        target_strings = [
            " " * leading_spaces[i] + s + " " * trailing_spaces[i]
            for i, s in enumerate(strings)
        ]
        target_df = pl.DataFrame({"id": ids, "name": target_strings})

        # Run comparison with ignore_spaces=True (default)
        config = ComparisonConfig(join_columns=["id"], ignore_spaces=True)
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # All rows should match since whitespace is stripped
        assert result.mismatched_rows == 0, (
            f"Expected 0 mismatched rows with ignore_spaces=True, "
            f"got {result.mismatched_rows}"
        )
        assert result.matching_rows == len(
            strings
        ), f"Expected {len(strings)} matching rows, got {result.matching_rows}"

    @given(
        strings=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("L", "N")),
                min_size=1,
                max_size=20,
            ),
            min_size=1,
            max_size=10,
        ),
        leading_spaces=st.lists(
            st.integers(min_value=1, max_value=5), min_size=1, max_size=10
        ),
    )
    @settings(max_examples=20, deadline=None)
    def test_whitespace_differences_detected_when_disabled(
        self, strings: list, leading_spaces: list
    ):
        """
        **Feature: data-validation-library, Property 12: Whitespace-Insensitive String Comparison**
        **Validates: Requirements 3.8**

        For any strings that differ in whitespace, they should NOT match
        when ignore_spaces is False.
        """
        # Ensure lists are same length
        min_len = min(len(strings), len(leading_spaces))
        strings = strings[:min_len]
        leading_spaces = leading_spaces[:min_len]

        ids = list(range(len(strings)))

        # Create source DataFrame with original strings
        source_df = pl.DataFrame({"id": ids, "name": strings})

        # Create target DataFrame with leading whitespace added
        target_strings = [" " * leading_spaces[i] + s for i, s in enumerate(strings)]
        target_df = pl.DataFrame({"id": ids, "name": target_strings})

        # Run comparison with ignore_spaces=False
        config = ComparisonConfig(join_columns=["id"], ignore_spaces=False)
        comparator = DataComparator(config)
        result = comparator.compare(source_df, target_df)

        # All rows should be mismatched since whitespace matters
        assert result.mismatched_rows == len(strings), (
            f"Expected {len(strings)} mismatched rows with ignore_spaces=False, "
            f"got {result.mismatched_rows}"
        )
