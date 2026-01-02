# Collaboration Features

LavenderTown includes collaboration features for teams to work together on data quality issues.

## Overview

Collaboration features enable:
- Adding annotations to findings
- Creating shareable reports
- Tracking issue status
- Team workflows

## Annotations

### Adding Annotations

Add comments and tags to findings:

```python
from lavendertown.collaboration.api import add_annotation
from lavendertown import Inspector

inspector = Inspector(df)
findings = inspector.detect()

# Add annotation to a finding
annotation = add_annotation(
    finding=findings[0],
    author="Data Team",
    comment="This looks like a data entry error",
    tags=["data-entry", "needs-review"],
    status="needs-investigation"
)
```

### Status Values

- `reviewed`: Finding has been reviewed
- `fixed`: Issue has been fixed
- `false_positive`: Not actually an issue
- `needs-investigation`: Requires further investigation

### Retrieving Annotations

Get annotations for a finding:

```python
from lavendertown.collaboration.api import get_annotations

annotations = get_annotations(finding)

for ann in annotations:
    print(f"{ann.author}: {ann.comment}")
    print(f"Tags: {ann.tags}")
    print(f"Status: {ann.status}")
```

## Shareable Reports

### Creating Reports

Create reports to share with team members:

```python
from lavendertown.collaboration.api import create_shareable_report

report = create_shareable_report(
    title="Q4 Data Quality Report",
    author="Data Team",
    findings=findings,
    annotations=annotations
)
```

### Exporting Reports

Export reports to JSON files:

```python
from lavendertown.collaboration.api import export_report

report_path = export_report(report)
print(f"Report saved to: {report_path}")
```

### Importing Reports

Import previously exported reports:

```python
from lavendertown.collaboration.api import import_report

report = import_report("report.json")

print(f"Title: {report.title}")
print(f"Author: {report.author}")
print(f"Findings: {len(report.findings)}")
print(f"Annotations: {len(report.annotations)}")
```

## UI Integration

Collaboration features are integrated into the Streamlit UI:

1. Run your app with `inspector.render()`
2. Select a finding in the findings table
3. Add annotations through the UI
4. Create and export reports
5. Import reports from other team members

## Storage

Annotations and reports are stored in a `.lavendertown/` directory:

```
.lavendertown/
├── annotations/
│   └── [finding_id].json
└── reports/
    └── [report_id].json
```

**Note:** The `.lavendertown/` directory is automatically created and should be added to `.gitignore` to avoid committing collaboration data.

## Workflow Example

```python
from lavendertown import Inspector
from lavendertown.collaboration.api import (
    add_annotation,
    create_shareable_report,
    export_report
)

# Analyze data
inspector = Inspector(df)
findings = inspector.detect()

# Add annotations
for finding in findings[:3]:  # Annotate first 3 findings
    add_annotation(
        finding=finding,
        author="Analyst",
        comment="Needs data source verification",
        tags=["verification", "critical"],
        status="needs-investigation"
    )

# Create report
report = create_shareable_report(
    title="Weekly Data Quality Review",
    author="Data Team",
    findings=findings
)

# Export for sharing
report_path = export_report(report)
print(f"Report ready: {report_path}")
```

## CLI Integration

Collaboration features are available via CLI:

```bash
# Share a report
lavendertown share report.json

# Import a report
lavendertown import-report report.json
```

## Best Practices

1. **Use descriptive comments**: Explain why an issue is important
2. **Tag appropriately**: Use consistent tags across the team
3. **Update status**: Keep status current as issues are resolved
4. **Regular reports**: Create regular reports for stakeholders
5. **Version control**: Track report versions for historical reference

## Next Steps

- Learn about [Basic Usage](basic-usage.md) for general data quality analysis
- See [API Reference](../api-reference/collaboration/api.md) for detailed documentation

