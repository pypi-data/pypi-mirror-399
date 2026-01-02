# Custom Rules

!!! info "Version"
    Custom rules were introduced in **v0.2.0**. Cross-column rules were added in **v0.2.0**.

LavenderTown allows you to create custom data quality rules beyond the built-in detectors. Rules can be created through the UI or programmatically.

## Rule Types

### Range Rules

Validate that numeric values fall within a specified range:

```python
from lavendertown.rules.executors import RangeRule

rule = RangeRule(
    name="price_range",
    description="Price must be between 0 and 1000",
    column="price",
    min_value=0.0,
    max_value=1000.0
)
```

### Regex Rules

Validate string patterns using regular expressions:

```python
from lavendertown.rules.executors import RegexRule

rule = RegexRule(
    name="email_format",
    description="Email must match standard format",
    column="email",
    pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)
```

### Enum Rules

Validate that values are from an allowed set:

```python
from lavendertown.rules.executors import EnumRule

rule = EnumRule(
    name="valid_status",
    description="Status must be one of the allowed values",
    column="status",
    allowed_values=["active", "inactive", "pending"]
)
```

## Using Rules

### Programmatically

```python
from lavendertown.rules.models import RuleSet
from lavendertown.rules.executors import RangeRule
from lavendertown.detectors.rule_based import RuleBasedDetector
from lavendertown import Inspector

# Create ruleset
ruleset = RuleSet(name="my_rules", description="Custom validation rules")

# Add rules
ruleset.add_rule(RangeRule(
    name="age_range",
    description="Age must be between 0 and 120",
    column="age",
    min_value=0.0,
    max_value=120.0
))

# Create detector
rule_detector = RuleBasedDetector(ruleset)

# Use with Inspector
inspector = Inspector(df, detectors=[rule_detector])
findings = inspector.detect()
```

### Through the UI

1. Run your Streamlit app with `inspector.render()`
2. Click "Manage Rules" in the sidebar
3. Click "Create New Rule"
4. Select rule type and configure parameters
5. Rules execute automatically with each analysis

## RuleSet Management

### Saving and Loading Rules

```python
from lavendertown.rules.storage import save_ruleset, load_ruleset

# Save ruleset
save_ruleset(ruleset, "my_rules.json")

# Load ruleset
loaded_ruleset = load_ruleset("my_rules.json")
```

### Exporting Rules

Rules can be exported to other formats:

```python
from lavendertown.export.pandera import export_ruleset_to_pandera
from lavendertown.export.great_expectations import export_ruleset_to_great_expectations_json

# Export to Pandera
pandera_schema = export_ruleset_to_pandera(ruleset)

# Export to Great Expectations
ge_suite = export_ruleset_to_great_expectations_json(ruleset, "my_suite")
```

## Rule Execution

Rules are executed by the `RuleBasedDetector`, which:

1. Validates that required columns exist
2. Applies each rule to the DataFrame
3. Returns `GhostFinding` objects for violations
4. Handles both Pandas and Polars DataFrames

## Best Practices

1. **Name rules clearly**: Use descriptive names that explain what the rule checks
2. **Provide descriptions**: Help users understand the purpose of each rule
3. **Test rules**: Verify rules work correctly with sample data
4. **Organize rulesets**: Group related rules together in rulesets
5. **Version control**: Save rulesets to JSON files and track them in version control

## Next Steps

- Learn about [Cross-Column Rules](cross-column-rules.md) for multi-column validation
- See [API Reference](../api-reference/rules/executors.md) for detailed rule documentation

