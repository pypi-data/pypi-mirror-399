"""ML-assisted anomaly detection example.

This example demonstrates how to use LavenderTown's MLAnomalyDetector
to identify anomalies using machine learning algorithms.
"""

import pandas as pd
import streamlit as st

try:
    import sklearn  # noqa: F401
except ImportError:
    st.error(
        "❌ scikit-learn is not installed. Install it with: `pip install lavendertown[ml]`"
    )
    st.stop()

from lavendertown import Inspector
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector

st.title("ML-Assisted Anomaly Detection Example")

st.markdown(
    """
    This example shows how to detect anomalies using machine learning algorithms:
    - **Isolation Forest**: Good for general anomaly detection
    - **Local Outlier Factor (LOF)**: Density-based detection
    - **One-Class SVM**: Boundary-based detection
    
    **Note:** Install scikit-learn for ML features:
    ```bash
    pip install lavendertown[ml]
    ```
    """
)

# Create sample data with anomalies
data = {
    "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 50, 2, 3, 4, 5],  # 50 is an anomaly
    "feature2": [
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        100,
        12,
        13,
        14,
    ],  # 100 is an anomaly
    "feature3": [
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        200,
        103,
        104,
    ],  # 200 is an anomaly
    "category": [
        "A",
        "B",
        "A",
        "B",
        "A",
        "B",
        "A",
        "B",
        "A",
        "B",
        "A",
        "B",
        "A",
        "B",
        "A",
    ],
}

df = pd.DataFrame(data)

# Display the data
st.subheader("Sample Data")
st.dataframe(df)

# Show data distribution
st.markdown("### Data Distribution")
col1, col2, col3 = st.columns(3)
with col1:
    st.bar_chart(df["feature1"])
with col2:
    st.bar_chart(df["feature2"])
with col3:
    st.bar_chart(df["feature3"])

# Create inspector with ML detector
st.subheader("ML Anomaly Detection")

algorithm = st.selectbox(
    "ML Algorithm",
    ["isolation_forest", "lof", "one_class_svm"],
    help="Choose the ML algorithm for anomaly detection",
)

contamination = st.slider(
    "Expected Anomaly Proportion",
    min_value=0.01,
    max_value=0.5,
    value=0.1,
    step=0.01,
    help="Expected proportion of anomalies (0.01 = 1%, 0.5 = 50%)",
)

# Create ML detector
detector = MLAnomalyDetector(
    algorithm=algorithm,
    contamination=contamination,
    random_state=42,
)

# Create inspector with custom detector
inspector = Inspector(df, detectors=[detector])

st.markdown("### Detection Results")
inspector.render()

st.info(
    "💡 **Tip:** ML-assisted anomaly detection is useful for finding complex "
    "anomalies that may not be obvious with statistical methods. It works well "
    "with multi-dimensional data and can detect subtle patterns."
)
