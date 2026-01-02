"""Helper functions for generating realistic test data using Faker.

This module provides utilities for generating test DataFrames with realistic
data for use in examples, tests, and documentation.
"""

from __future__ import annotations

import pandas as pd

try:
    from faker import Faker

    _FAKER_AVAILABLE = True
except ImportError:
    _FAKER_AVAILABLE = False
    Faker = None  # type: ignore[assignment,misc]


def generate_realistic_dataframe(
    n_rows: int,
    columns: dict[str, str],
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate a realistic DataFrame using Faker.

    Creates a DataFrame with realistic test data based on column specifications.
    Each column type is mapped to a Faker provider.

    Args:
        n_rows: Number of rows to generate. Must be positive.
        columns: Dictionary mapping column names to data types. Valid types:
            - "name": Full names
            - "email": Email addresses
            - "date": Dates (YYYY-MM-DD)
            - "datetime": Datetime strings (ISO format)
            - "address": Street addresses
            - "city": City names
            - "country": Country names
            - "phone": Phone numbers
            - "text": Random text
            - "int": Random integers (0-1000)
            - "float": Random floats (0-100)
            - "bool": Boolean values
        seed: Random seed for reproducibility. None for random data.

    Returns:
        pandas.DataFrame with generated data

    Raises:
        ImportError: If Faker is not installed. Install with:
            pip install lavendertown[dev]
        ValueError: If n_rows is not positive or column type is invalid

    Example:
        Generate a DataFrame with names and emails::

            df = generate_realistic_dataframe(
                100,
                {"name": "name", "email": "email", "age": "int"},
                seed=42
            )
    """
    if not _FAKER_AVAILABLE:
        raise ImportError(
            "Faker is required for realistic data generation. "
            "Install with: pip install lavendertown[dev]"
        )

    if n_rows < 0:
        raise ValueError(f"n_rows must be non-negative, got {n_rows}")

    fake = Faker()
    if seed is not None:
        Faker.seed(seed)

    # Map column types to Faker providers
    type_map = {
        "name": lambda: fake.name(),
        "email": lambda: fake.email(),
        "date": lambda: str(
            fake.date_object()
        ),  # Returns date object, convert to string
        "datetime": lambda: fake.date_time().isoformat(),
        "address": lambda: fake.address().replace("\n", ", "),
        "city": lambda: fake.city(),
        "country": lambda: fake.country(),
        "phone": lambda: fake.phone_number(),
        "text": lambda: fake.text(max_nb_chars=100),
        "int": lambda: fake.random_int(min=0, max=1000),
        "float": lambda: fake.random_number(digits=2) / 100.0,
        "bool": lambda: fake.boolean(),
    }

    # Validate column types
    valid_types = set(type_map.keys())
    invalid_types = [col for col, dtype in columns.items() if dtype not in valid_types]
    if invalid_types:
        raise ValueError(
            f"Invalid column types: {invalid_types}. "
            f"Valid types are: {sorted(valid_types)}"
        )

    # Generate data
    data: dict[str, list] = {}
    for col_name, col_type in columns.items():
        generator = type_map[col_type]
        data[col_name] = [generator() for _ in range(n_rows)]

    return pd.DataFrame(data)


def generate_dataframe_with_issues(
    n_rows: int,
    issue_types: list[str] | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate a DataFrame with realistic data and injected data quality issues.

    Creates a DataFrame with realistic test data and optionally injects common
    data quality issues like nulls, outliers, type inconsistencies, etc.

    Args:
        n_rows: Number of rows to generate. Must be positive.
        issue_types: List of issue types to inject. Valid options:
            - "nulls": Add null values to some columns
            - "outliers": Add outlier values to numeric columns
            - "type_inconsistency": Mix types in some columns
            - None: No issues injected (default)
        seed: Random seed for reproducibility. None for random data.

    Returns:
        pandas.DataFrame with generated data and injected issues

    Raises:
        ImportError: If Faker is not installed
        ValueError: If n_rows is not positive or issue_type is invalid

    Example:
        Generate data with nulls and outliers::

            df = generate_dataframe_with_issues(
                100,
                issue_types=["nulls", "outliers"],
                seed=42
            )
    """
    if issue_types is None:
        issue_types = []

    # Generate base realistic data
    columns = {
        "name": "name",
        "email": "email",
        "age": "int",
        "salary": "float",
        "active": "bool",
        "join_date": "date",
    }
    # Handle seed for Faker - need to reset seed for each generation
    if seed is not None:
        import random

        random.seed(seed)
    df = generate_realistic_dataframe(n_rows, columns, seed=seed)

    # Inject issues
    if "nulls" in issue_types:
        # Add nulls to 10% of rows in some columns
        import random

        if seed is not None:
            random.seed(seed)
        null_indices = random.sample(range(n_rows), k=min(n_rows // 10, n_rows))
        for idx in null_indices:
            df.loc[idx, "email"] = None  # type: ignore[call-overload]

    if "outliers" in issue_types:
        # Add outliers to numeric columns
        import random

        if seed is not None:
            random.seed(seed + 1)
        outlier_indices = random.sample(range(n_rows), k=min(n_rows // 20, n_rows))
        for idx in outlier_indices:
            df.loc[idx, "salary"] = df["salary"].max() * 10  # type: ignore[call-overload]

    if "type_inconsistency" in issue_types:
        # Mix types in some columns
        import random

        if seed is not None:
            random.seed(seed + 2)
        mixed_indices = random.sample(range(n_rows), k=min(n_rows // 15, n_rows))
        for idx in mixed_indices:
            df.loc[idx, "age"] = "invalid_age"  # type: ignore[call-overload]

    return df
