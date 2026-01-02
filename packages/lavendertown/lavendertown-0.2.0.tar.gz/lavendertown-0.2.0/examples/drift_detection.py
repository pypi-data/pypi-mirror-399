"""Dataset comparison and drift detection example.

This example demonstrates how to compare two datasets and detect
schema and distribution changes using LavenderTown's drift detection.
"""

import pandas as pd
import streamlit as st

from lavendertown import Inspector

st.title("Dataset Drift Detection Example")

st.markdown(
    """
    This example shows how to compare two datasets and detect:
    - Schema changes (new/removed columns, type changes)
    - Distribution changes (null percentages, ranges, cardinality)
    """
)

# Create baseline dataset
baseline_data = {
    "customer_id": [1, 2, 3, 4, 5],
    "age": [25, 30, 35, 40, 45],
    "email": [
        "alice@example.com",
        "bob@example.com",
        "charlie@example.com",
        "david@example.com",
        "eve@example.com",
    ],
    "purchase_amount": [100.50, 200.00, 150.75, 300.00, 250.50],
    "category": ["A", "B", "A", "C", "A"],
}

baseline_df = pd.DataFrame(baseline_data)

# Create current dataset with changes
current_data = {
    "customer_id": [1, 2, 3, 4, 5, 6],  # New row
    "age": [25, 30, 35, 40, 45, 50],  # New row
    "email": [
        "alice@example.com",
        "bob@example.com",
        None,  # New null
        "david@example.com",
        "eve@example.com",
        "frank@example.com",  # New row
    ],
    "purchase_amount": [
        100.50,
        250.00,
        150.75,
        400.00,
        250.50,
        500.00,
    ],  # Changed values
    "category": ["A", "B", "A", "C", "A", "B"],  # New row
    "new_column": [1, 2, 3, 4, 5, 6],  # New column added
}

current_df = pd.DataFrame(current_data)

# Display datasets
col1, col2 = st.columns(2)

with col1:
    st.subheader("Baseline Dataset")
    st.dataframe(baseline_df)
    st.caption(f"Shape: {baseline_df.shape}")

with col2:
    st.subheader("Current Dataset")
    st.dataframe(current_df)
    st.caption(f"Shape: {current_df.shape}")

# Perform drift detection
st.subheader("Drift Detection Results")

inspector = Inspector(current_df)

# Compare datasets
drift_findings = inspector.compare_with_baseline(
    baseline_df=baseline_df,
    comparison_type="full",  # Can be "full", "schema_only", or "distribution_only"
)

# Display drift findings summary
st.markdown("### Drift Summary")

drift_count = len([f for f in drift_findings if f.ghost_type == "drift"])
st.metric("Total Drift Issues Detected", drift_count)

if drift_findings:
    # Group by drift type
    schema_findings = [
        f for f in drift_findings if f.metadata.get("drift_type") == "schema"
    ]
    distribution_findings = [
        f for f in drift_findings if f.metadata.get("drift_type") == "distribution"
    ]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Schema Changes", len(schema_findings))
    with col2:
        st.metric("Distribution Changes", len(distribution_findings))

    # Display detailed findings
    st.markdown("### Detailed Findings")

    for finding in drift_findings:
        if finding.ghost_type == "drift":
            with st.expander(f"{finding.severity.upper()}: {finding.column}"):
                st.write(f"**Description:** {finding.description}")
                st.write(
                    f"**Change Type:** {finding.metadata.get('change_type', 'N/A')}"
                )
                if finding.metadata:
                    st.json(finding.metadata)
else:
    st.info("No drift detected between the datasets.")

# Also show regular quality findings
st.subheader("Current Dataset Quality Analysis")
inspector.render()
