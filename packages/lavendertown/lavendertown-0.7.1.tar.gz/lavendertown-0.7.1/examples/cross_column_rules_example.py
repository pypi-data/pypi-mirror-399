"""Cross-column validation rules example.

This example demonstrates how to use LavenderTown's CrossColumnRule
to validate relationships between multiple columns.
"""

import pandas as pd
import streamlit as st

from lavendertown import Inspector
from lavendertown.detectors.rule_based import RuleBasedDetector
from lavendertown.rules.cross_column import CrossColumnRule
from lavendertown.rules.models import RuleSet

st.title("Cross-Column Validation Rules Example")

st.markdown(
    """
    This example shows how to create cross-column validation rules that check
    relationships between multiple columns:
    - **Equals**: Two columns must have equal values
    - **Greater/Less Than**: One column must be greater/less than another
    - **Sum Equals**: Sum of columns must equal a target column
    - **Conditional**: If-then logic (if col1 == X then col2 == Y)
    - **Referential Integrity**: Values in one column must exist in another
    """
)

# Create sample data with cross-column relationships
data = {
    "order_id": [1, 2, 3, 4, 5, 6],
    "quantity": [10, 20, 30, 40, 50, 60],
    "unit_price": [5.0, 10.0, 15.0, 20.0, 25.0, 30.0],
    "subtotal": [50.0, 200.0, 450.0, 800.0, 1250.0, 1800.0],  # Some don't match
    "discount": [0.0, 0.1, 0.0, 0.2, 0.0, 0.15],
    "total": [50.0, 180.0, 450.0, 640.0, 1250.0, 1530.0],  # Some don't match
    "status": ["pending", "pending", "completed", "pending", "completed", "pending"],
    "payment_date": [
        None,
        None,
        "2024-01-15",
        None,
        "2024-01-20",
        None,
    ],  # Should be set when completed (for demonstration)
    "category": ["A", "B", "A", "C", "B", "A"],
    "valid_categories": ["A", "B", "C", "A", "B", "A"],  # Reference column
}

df = pd.DataFrame(data)

# Display the data
st.subheader("Sample Data")
st.dataframe(df)

# Create cross-column rules
st.subheader("Cross-Column Rules")

ruleset = RuleSet(
    name="cross_column_example", description="Cross-column validation rules"
)

# Rule 1: Subtotal should equal quantity * unit_price
ruleset.add_rule(  # type: ignore[arg-type]
    CrossColumnRule(  # type: ignore[arg-type]
        name="subtotal_check",
        description="Subtotal must equal quantity * unit_price",
        source_columns=["quantity", "unit_price"],
        operation="sum_equals",
        target_column="subtotal",
    )
)

# Rule 2: Total should be less than or equal to subtotal (after discount)
ruleset.add_rule(  # type: ignore[arg-type]
    CrossColumnRule(  # type: ignore[arg-type]
        name="total_check",
        description="Total should be less than or equal to subtotal",
        source_columns=["total", "subtotal"],
        operation="less_than",
    )
)

# Rule 3: If status is "completed", payment_date should be set
# Note: Conditional rules check if-then logic. For null checks, we'd need
# a different approach or custom rule. This example shows the pattern.
ruleset.add_rule(  # type: ignore[arg-type]
    CrossColumnRule(  # type: ignore[arg-type]
        name="payment_date_check",
        description="If status is 'completed', payment_date must be set",
        source_columns=["status", "payment_date"],
        operation="conditional",
        condition={
            "if_column": "status",
            "if_value": "completed",
            "then_column": "payment_date",
            "then_value": "2024-01-01",  # Example: check for a specific value
        },
    )
)

# Rule 4: Category must exist in valid_categories (referential integrity)
ruleset.add_rule(  # type: ignore[arg-type]
    CrossColumnRule(  # type: ignore[arg-type]
        name="category_referential",
        description="Category values must exist in valid_categories",
        source_columns=["category"],
        operation="referential",
        target_column="valid_categories",
    )
)

# Display rules
st.markdown("### Defined Rules")
for rule in ruleset.rules:
    # Type cast to CrossColumnRule for attribute access
    from typing import cast

    cross_rule = cast(CrossColumnRule, rule)
    with st.expander(f"Rule: {cross_rule.name}"):
        st.write(f"**Description:** {cross_rule.description}")
        st.write(f"**Operation:** {cross_rule.operation}")
        st.write(f"**Source Columns:** {', '.join(cross_rule.source_columns)}")
        if cross_rule.target_column:
            st.write(f"**Target Column:** {cross_rule.target_column}")
        if cross_rule.condition:
            st.write(f"**Condition:** {cross_rule.condition}")

# Create inspector with ruleset
st.subheader("Validation Results")
inspector = Inspector(df)
inspector.render()

# Execute rules
st.markdown("### Cross-Column Rule Validation")

rule_detector = RuleBasedDetector(ruleset)  # type: ignore[arg-type]
rule_findings = rule_detector.detect(df)

if rule_findings:
    st.warning(f"Found {len(rule_findings)} cross-column rule violations:")
    for finding in rule_findings:
        st.error(f"**{finding.column}**: {finding.description}")
        if finding.metadata:
            st.json(finding.metadata)
else:
    st.success("✅ All cross-column rules passed!")

st.info(
    "💡 **Tip:** Cross-column rules are powerful for validating business logic "
    "and data relationships. Use them to ensure data consistency across "
    "multiple columns."
)
