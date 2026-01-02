"""Programmatic usage example for LavenderTown.

This example shows how to use LavenderTown programmatically
without the Streamlit UI, useful for scripts and automated workflows.
"""

import pandas as pd
from lavendertown import Inspector

# Create sample data
data = {
    "product_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "price": [10.99, 25.50, None, 45.00, -5.00, 100.00, 200.00, 300.00],
    "quantity": [100, 50, 75, None, 200, 150, 0, 300],
    "category": ["A", "B", "A", "C", "A", "B", "A", "C"],
}

df = pd.DataFrame(data)

# Create inspector
inspector = Inspector(df)

# Get findings programmatically (no UI)
print("=" * 60)
print("Data Quality Analysis Results")
print("=" * 60)

findings = inspector.detect()

# Group findings by severity
by_severity = {}
for finding in findings:
    severity = finding.severity
    if severity not in by_severity:
        by_severity[severity] = []
    by_severity[severity].append(finding)

# Print summary
print(f"\nTotal findings: {len(findings)}")
print("\nBy severity:")
for severity in ["error", "warning", "info"]:
    if severity in by_severity:
        print(f"  {severity.upper()}: {len(by_severity[severity])}")

# Print detailed findings
print("\n" + "=" * 60)
print("Detailed Findings")
print("=" * 60)

for severity in ["error", "warning", "info"]:
    if severity not in by_severity:
        continue

    print(f"\n{severity.upper()} Issues:")
    print("-" * 60)

    for finding in by_severity[severity]:
        print(f"\nColumn: {finding.column}")
        print(f"Type: {finding.ghost_type}")
        print(f"Description: {finding.description}")

        if finding.row_indices:
            print(f"Affected rows: {finding.row_indices}")
            print(f"Count: {len(finding.row_indices)}")

        if finding.metadata:
            print(f"Metadata: {finding.metadata}")

# Example: Filter and process specific findings
print("\n" + "=" * 60)
print("Processing Specific Findings")
print("=" * 60)

# Get all null-related findings
null_findings = [f for f in findings if f.ghost_type == "null"]
print(f"\nFound {len(null_findings)} null-related issues:")

for finding in null_findings:
    print(f"  - {finding.column}: {finding.description}")

# Get all outlier findings
outlier_findings = [f for f in findings if f.ghost_type == "outlier"]
print(f"\nFound {len(outlier_findings)} outlier issues:")

for finding in outlier_findings:
    print(f"  - {finding.column}: {finding.description}")
