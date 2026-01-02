"""Polars DataFrame example for LavenderTown.

This example demonstrates how to use LavenderTown with Polars DataFrames
for better performance on large datasets.
"""

import streamlit as st

try:
    import polars as pl
except ImportError:
    st.error(
        "❌ Polars is not installed. Install it with: `pip install lavendertown[polars]`"
    )
    st.stop()

from lavendertown import Inspector

st.title("LavenderTown with Polars Example")

st.markdown(
    """
    This example shows how to use LavenderTown with Polars DataFrames.
    Polars provides better performance for large datasets.
    
    **Note:** Install Polars support with: `pip install lavendertown[polars]`
    """
)

# Create sample data with Polars
data = {
    "id": list(range(1, 1001)),  # 1000 rows
    "value": [i * 1.5 if i % 100 != 0 else None for i in range(1, 1001)],  # Some nulls
    "category": [f"cat_{i % 10}" for i in range(1, 1001)],
    "score": [i * 2.0 + (i % 50) * 10 for i in range(1, 1001)],  # Some outliers
}

# Create Polars DataFrame
df = pl.DataFrame(data)

# Display info
st.subheader("Dataset Information")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Rows", len(df))
with col2:
    st.metric("Columns", len(df.columns))
with col3:
    st.metric("Backend", "Polars")

st.markdown("### Sample Data")
st.dataframe(df.head(10).to_pandas())  # Convert to pandas for Streamlit display

# Display schema
st.markdown("### Schema")
st.code(str(df.schema), language="python")

# Create inspector (automatically detects Polars)
st.subheader("Data Quality Analysis")
st.markdown("LavenderTown automatically detects that this is a Polars DataFrame.")

inspector = Inspector(df)
inspector.render()

st.info(
    "💡 Tip: Polars is typically 5-10x faster than Pandas for large datasets. "
    "Use Polars when working with datasets >100k rows."
)
