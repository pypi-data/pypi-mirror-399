"""Basic usage example for LavenderTown.

This example demonstrates the simplest way to use LavenderTown
to analyze data quality in a Pandas DataFrame.
"""

import pandas as pd
import streamlit as st

from lavendertown import Inspector

# Create sample data with various data quality issues
data = {
    "name": ["Alice", "Bob", None, "David", "Eve"],
    "age": [25, 30, None, 45, -5],  # Negative age issue
    "email": [
        "alice@example.com",
        "invalid-email",  # Invalid email format
        "charlie@example.com",
        "david@example.com",
        "eve@example.com",
    ],
    "score": [85, 92, 78, 105, 88],  # Score > 100 issue
    "category": ["A", "B", "A", "C", "A"],
}

df = pd.DataFrame(data)

st.title("LavenderTown Basic Usage Example")

st.markdown(
    """
    This example shows how to use LavenderTown to detect data quality issues.
    The dataset contains various problems:
    - Missing values (nulls)
    - Invalid values (negative age, score > 100)
    - Type inconsistencies
    """
)

# Display the data
st.subheader("Sample Data")
st.dataframe(df)

# Create inspector and render
st.subheader("Data Quality Analysis")
inspector = Inspector(df)
inspector.render()
