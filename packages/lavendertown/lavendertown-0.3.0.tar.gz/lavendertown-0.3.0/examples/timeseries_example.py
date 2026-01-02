"""Time-series anomaly detection example.

This example demonstrates how to use LavenderTown's TimeSeriesAnomalyDetector
to identify anomalies in time-series data.
"""

import pandas as pd
import streamlit as st

from lavendertown import Inspector
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector

st.title("Time-Series Anomaly Detection Example")

st.markdown(
    """
    This example shows how to detect anomalies in time-series data using:
    - **Z-score method**: Detects values that deviate significantly from the mean
    - **Moving average method**: Detects values that deviate from a rolling average
    - **Seasonal decomposition**: Detects anomalies after removing seasonal patterns
    
    **Note:** Install statsmodels for seasonal decomposition:
    ```bash
    pip install lavendertown[timeseries]
    ```
    """
)

# Create sample time-series data with anomalies
dates = pd.date_range("2024-01-01", periods=100, freq="D")
values = []

# Generate normal time-series with trend and some noise
for i in range(100):
    base_value = 100 + i * 0.5  # Trend
    noise = (i % 7 - 3) * 2  # Weekly pattern
    random_noise = (i % 13) * 0.3  # Some randomness
    value = base_value + noise + random_noise
    values.append(value)

# Add some anomalies
values[20] = 200  # Sudden spike
values[45] = 50  # Sudden drop
values[70] = 180  # Another spike
values[85] = 40  # Another drop

data = {"date": dates, "value": values, "category": ["A"] * 100}
df = pd.DataFrame(data)

# Display the data
st.subheader("Sample Time-Series Data")
st.dataframe(df.head(20))

# Show the time-series chart
st.markdown("### Time-Series Visualization")
st.line_chart(df.set_index("date")["value"])

# Create inspector with time-series detector
st.subheader("Anomaly Detection")

method = st.selectbox(
    "Detection Method",
    ["zscore", "moving_avg", "seasonal"],
    help="Choose the anomaly detection method",
)

sensitivity = st.slider(
    "Sensitivity",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.5,
    help="Higher values detect fewer anomalies (for z-score, this is standard deviations)",
)

window_size = st.slider(
    "Window Size (for moving average)",
    min_value=5,
    max_value=30,
    value=10,
    step=1,
    help="Window size for moving average method",
)

# Create time-series detector
detector = TimeSeriesAnomalyDetector(
    datetime_column="date",
    method=method,
    sensitivity=sensitivity,
    window_size=window_size,
)

# Create inspector with custom detector
inspector = Inspector(df, detectors=[detector])

st.markdown("### Detection Results")
inspector.render()

st.info(
    "💡 **Tip:** Time-series anomaly detection is useful for monitoring data quality "
    "over time, detecting sudden changes, and identifying unusual patterns in "
    "temporal data."
)
