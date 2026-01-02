# Cross-Column Rules

Cross-column rules validate relationships between multiple columns, enabling complex business logic validation.

## Overview

Cross-column rules check relationships across columns, such as:
- Equality between columns
- Arithmetic relationships (sum, difference)
- Conditional logic (if-then rules)
- Referential integrity

## Rule Operations

### Equals

Check that two columns have equal values:

```python
from lavendertown.rules.cross_column import CrossColumnRule

rule = CrossColumnRule(
    name="name_equality",
    description="First name and last name must match",
    source_columns=["first_name", "last_name"],
    operation="equals"
)
```

### Comparison Operations

Check that one column is greater than or less than another:

```python
# Greater than
rule = CrossColumnRule(
    name="price_check",
    description="Total must be greater than subtotal",
    source_columns=["total", "subtotal"],
    operation="greater_than"
)

# Less than
rule = CrossColumnRule(
    name="discount_check",
    description="Discount must be less than price",
    source_columns=["discount", "price"],
    operation="less_than"
)
```

### Arithmetic Operations

Validate arithmetic relationships:

```python
# Sum equals
rule = CrossColumnRule(
    name="subtotal_check",
    description="Subtotal must equal quantity * unit_price",
    source_columns=["quantity", "unit_price"],
    operation="sum_equals",
    target_column="subtotal"
)
```

### Conditional Logic

Implement if-then validation:

```python
rule = CrossColumnRule(
    name="payment_date_check",
    description="If status is 'completed', payment_date must be set",
    source_columns=["status", "payment_date"],
    operation="conditional",
    condition={
        "if_column": "status",
        "if_value": "completed",
        "then_column": "payment_date",
        "then_value": "not_null"  # Special value for null check
    }
)
```

### Referential Integrity

Validate that values in one column exist in another:

```python
rule = CrossColumnRule(
    name="category_referential",
    description="Category values must exist in valid_categories",
    source_columns=["category"],
    operation="referential",
    target_column="valid_categories"
)
```

## Using Cross-Column Rules

### Programmatically

```python
from lavendertown.rules.models import RuleSet
from lavendertown.rules.cross_column import CrossColumnRule
from lavendertown.detectors.rule_based import RuleBasedDetector
from lavendertown import Inspector

# Create ruleset
ruleset = RuleSet(name="cross_column_rules", description="Multi-column validation")

# Add cross-column rule
ruleset.add_rule(CrossColumnRule(
    name="total_validation",
    description="Total must equal sum of line items",
    source_columns=["item1", "item2", "item3"],
    operation="sum_equals",
    target_column="total"
))

# Use with Inspector
rule_detector = RuleBasedDetector(ruleset)
inspector = Inspector(df, detectors=[rule_detector])
findings = inspector.detect()
```

### Through the UI

1. Run your Streamlit app with `inspector.render()`
2. Click "Manage Rules" in the sidebar
3. Click "Create New Rule"
4. Select "Cross-Column" rule type
5. Configure source columns, operation, and target column
6. Rules execute automatically with each analysis

## Supported Operations

| Operation | Description | Source Columns | Target Column |
|-----------|-------------|----------------|---------------|
| `equals` | Column A equals Column B | 2 | No |
| `greater_than` | Column A > Column B | 2 | No |
| `less_than` | Column A < Column B | 2 | No |
| `sum_equals` | Sum of source columns equals target | 2+ | Yes |
| `conditional` | If condition met, then check another | 2+ | No |
| `referential` | Values in source exist in target | 1 | Yes |

## Examples

### Order Validation

```python
ruleset = RuleSet(name="order_validation")

# Subtotal check
ruleset.add_rule(CrossColumnRule(
    name="subtotal",
    description="Subtotal must equal quantity * unit_price",
    source_columns=["quantity", "unit_price"],
    operation="sum_equals",
    target_column="subtotal"
))

# Total check
ruleset.add_rule(CrossColumnRule(
    name="total",
    description="Total must be less than or equal to subtotal",
    source_columns=["total", "subtotal"],
    operation="less_than"
))
```

### Conditional Validation

```python
# If order is completed, payment date must be set
ruleset.add_rule(CrossColumnRule(
    name="payment_required",
    description="Completed orders must have payment date",
    source_columns=["status", "payment_date"],
    operation="conditional",
    condition={
        "if_column": "status",
        "if_value": "completed",
        "then_column": "payment_date",
        "then_value": "not_null"
    }
))
```

## Best Practices

1. **Use descriptive names**: Clearly indicate what relationship is being validated
2. **Validate column existence**: Ensure all referenced columns exist in your data
3. **Handle nulls**: Consider how null values should be handled in your rules
4. **Test thoroughly**: Verify rules work correctly with various data scenarios
5. **Document business logic**: Use descriptions to explain why rules exist

## Next Steps

- Learn about [Custom Rules](custom-rules.md) for single-column validation
- See [API Reference](../api-reference/rules/cross_column.md) for detailed documentation

