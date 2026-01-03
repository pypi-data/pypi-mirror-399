# PyCaroline

[![PyPI version](https://badge.fury.io/py/pycaroline.svg)](https://badge.fury.io/py/pycaroline)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/ryankarlos/pycaroline/actions/workflows/test.yml/badge.svg)](https://github.com/ryankarlos/pycaroline/actions)
[![Codecov](https://codecov.io/gh/ryankarlos/pycaroline/graph/badge.svg?token=nfQT3lqoc8)](https://codecov.io/gh/ryankarlos/pycaroline)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://ryankarlos.github.io/pycaroline)

A Python library for validating data migrations between cloud data warehouses. Built on [datacompy](https://github.com/capitalone/datacompy), PyCaroline provides a unified interface for connecting[...]

*Named in honor of Caroline* 💜

## Why PyCaroline?

Data migrations are risky. Whether you're moving from Snowflake to BigQuery, consolidating data warehouses, or validating ETL pipelines, you need confidence that your data arrived intact. PyCaroli[...]

## Features

- 🔌 **Multi-database support** - Snowflake, BigQuery, Redshift with unified API
- 🔍 **Flexible comparison** - Row-level and column-level with configurable tolerances
- 📊 **Rich reports** - JSON summaries, CSV details, and beautiful HTML reports
- 🖥️ **CLI & Python API** - Use from command line or integrate into your code
- ⚙️ **Configuration-driven** - YAML config with environment variable substitution
- 🧪 **Well-tested** - 90%+ test coverage with property-based tests
- 🐍 **Modern Python** - Supports Python 3.12 and 3.13

## Installation

```bash
# Using uv (recommended)
uv add pycaroline

# Using pip
pip install pycaroline
```

### With Database-Specific Dependencies

```bash
# Snowflake
uv add "pycaroline[snowflake]"

# BigQuery
uv add "pycaroline[bigquery]"

# Redshift
uv add "pycaroline[redshift]"

# All databases
uv add "pycaroline[all]"
```

## Quick Start

### Python API

```python
from pycaroline import DataValidator, ConfigLoader, DataComparator, ComparisonConfig
from pathlib import Path

# Using configuration file
config = ConfigLoader.load(Path("validation_config.yaml"))
validator = DataValidator(config)
results = validator.validate()

for table, result in results.items():
    print(f"{table}: {result.matching_rows}/{result.source_row_count} rows match")
```

### Direct DataFrame Comparison

```python
import polars as pl
from pycaroline import DataComparator, ComparisonConfig

source_df = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
target_df = pl.DataFrame({"id": [1, 2, 4], "value": ["a", "B", "d"]})

comparator = DataComparator(ComparisonConfig(
    join_columns=["id"],
    ignore_case=True,
    ignore_spaces=True,
))
result = comparator.compare(source_df, target_df)

print(f"Matching rows: {result.matching_rows}")
print(f"Rows only in source: {len(result.rows_only_in_source)}")
print(f"Rows only in target: {len(result.rows_only_in_target)}")
```

### Command Line

```bash
# Validate using config file
pycaroline validate --config validation_config.yaml --output ./reports

# Quick comparison
pycaroline compare \
    --source-type snowflake \
    --target-type bigquery \
    --source-table my_schema.customers \
    --target-table my_dataset.customers \
    --join-columns customer_id
```

## Configuration

Create a `validation_config.yaml`:

```yaml
source:
  type: snowflake
  connection:
    account: ${SNOWFLAKE_ACCOUNT}
    user: ${SNOWFLAKE_USER}
    password: ${SNOWFLAKE_PASSWORD}
    warehouse: ${SNOWFLAKE_WAREHOUSE}
    database: my_database

target:
  type: bigquery
  connection:
    project: ${GCP_PROJECT}
    credentials_path: ${GOOGLE_APPLICATION_CREDENTIALS}

tables:
  - source_table: customers
    target_table: customers
    join_columns: [customer_id]
    sample_size: 10000  # Optional: limit for large tables

comparison:
  abs_tol: 0.0001
  ignore_case: false
  ignore_spaces: true

output_dir: ./validation_results
```

## Report Output

```text
validation_results/
├── customers_summary.json       # Match statistics
├── customers_report.html        # Visual HTML report
├── customers_column_stats.csv   # Column-level stats
├── customers_rows_only_in_source.csv
├── customers_rows_only_in_target.csv
└── customers_mismatched_rows.csv
```

## Documentation

Full documentation is available at [https://yourusername.github.io/pycaroline](https://yourusername.github.io/pycaroline)

## API Reference

### Core Classes

| Class | Description |
|-------|-------------|
| `DataValidator` | Main orchestrator for validation workflows |
| `ConfigLoader` | Loads YAML configuration with env var substitution |
| `DataComparator` | Compares DataFrames using datacompy |
| `ReportGenerator` | Generates JSON, CSV, and HTML reports |
| `ConnectorFactory` | Factory for creating database connectors |

### Exceptions

| Exception | Description |
|-----------|-------------|
| `ValidationError` | Validation operation failed |
| `ConfigurationError` | Invalid configuration |
| `ConnectionError` | Database connection failed |
| `QueryError` | Query execution failed |

## Development

```bash
# Clone and install
git clone https://github.com/ryankarlos/pycaroline.git
cd pycaroline
uv sync --all-extras

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=pycaroline --cov-report=html

# Serve documentation locally
uv run mkdocs serve

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting PRs.

## License

MIT License - see [LICENSE](LICENSE) for details.
