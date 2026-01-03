"""Property-based tests for database connectors.

These tests validate universal properties of connectors using hypothesis.
"""

from unittest.mock import MagicMock

import polars as pl
from hypothesis import given, settings
from hypothesis import strategies as st

from pycaroline.connectors.base import BaseConnector


class MockConnector(BaseConnector):
    """Mock connector for testing base connector properties."""

    def __init__(self, query_results: pl.DataFrame = None):
        self._connection = None
        self._query_results = (
            query_results if query_results is not None else pl.DataFrame()
        )

    def connect(self) -> None:
        self._connection = MagicMock()

    def disconnect(self) -> None:
        self._connection = None

    def query(self, sql: str) -> pl.DataFrame:
        return self._query_results


class TestProperty3QueryReturnsDataFrame:
    """
    **Feature: data-validation-library, Property 3: Query Returns DataFrame**
    **Validates: Requirements 2.1**

    For any valid SQL SELECT query executed via query(), the result SHALL be
    a polars DataFrame instance.
    """

    @given(
        columns=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("L", "N")),
                min_size=1,
                max_size=10,
            ),
            min_size=1,
            max_size=5,
            unique=True,
        ),
        num_rows=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=100)
    def test_query_returns_dataframe_for_any_result_shape(
        self, columns: list, num_rows: int
    ):
        """
        **Feature: data-validation-library, Property 3: Query Returns DataFrame**
        **Validates: Requirements 2.1**

        For any valid query result with arbitrary columns and rows,
        the query() method must return a polars DataFrame.
        """
        # Create a DataFrame with the generated shape
        data = {col: list(range(num_rows)) for col in columns}
        expected_df = pl.DataFrame(data)

        # Create mock connector with this result
        connector = MockConnector(query_results=expected_df)
        connector.connect()

        # Execute query
        result = connector.query("SELECT * FROM test_table")

        # Verify result is a DataFrame
        assert isinstance(
            result, pl.DataFrame
        ), f"Expected polars DataFrame, got {type(result)}"

        connector.disconnect()

    @given(
        columns=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("L", "N")),
                min_size=1,
                max_size=10,
            ),
            min_size=1,
            max_size=5,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_empty_query_returns_dataframe_with_schema(self, columns: list):
        """
        **Feature: data-validation-library, Property 3: Query Returns DataFrame**
        **Validates: Requirements 2.1, 2.4**

        For any query returning no results, the result must still be a
        DataFrame with the correct column schema.
        """
        # Create empty DataFrame with columns
        expected_df = pl.DataFrame({col: [] for col in columns})

        connector = MockConnector(query_results=expected_df)
        connector.connect()

        result = connector.query("SELECT * FROM empty_table")

        assert isinstance(result, pl.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == columns

        connector.disconnect()

    @given(
        data_types=st.lists(
            st.sampled_from(["int", "float", "str", "bool"]),
            min_size=1,
            max_size=5,
        )
    )
    @settings(max_examples=100)
    def test_query_preserves_data_types_in_dataframe(self, data_types: list):
        """
        **Feature: data-validation-library, Property 3: Query Returns DataFrame**
        **Validates: Requirements 2.1**

        For any query result with various data types, the result must be
        a DataFrame that can represent those types.
        """
        # Create DataFrame with various types
        data = {}
        for i, dtype in enumerate(data_types):
            col_name = f"col_{i}"
            if dtype == "int":
                data[col_name] = [1, 2, 3]
            elif dtype == "float":
                data[col_name] = [1.1, 2.2, 3.3]
            elif dtype == "str":
                data[col_name] = ["a", "b", "c"]
            elif dtype == "bool":
                data[col_name] = [True, False, True]

        expected_df = pl.DataFrame(data)

        connector = MockConnector(query_results=expected_df)
        connector.connect()

        result = connector.query("SELECT * FROM typed_table")

        assert isinstance(result, pl.DataFrame)
        assert len(result.columns) == len(data_types)

        connector.disconnect()
