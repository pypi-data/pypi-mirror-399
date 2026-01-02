"""Rule authoring UI components."""

from __future__ import annotations

from lavendertown.logging_config import get_logger
from lavendertown.rules.executors import EnumRule, RangeRule, RegexRule
from lavendertown.rules.models import Rule, RuleSet
from lavendertown.rules.storage import ruleset_from_json, ruleset_to_json

logger = get_logger(__name__)


def render_rule_editor(st: object, columns: list[str]) -> Rule | None:
    """Render UI for creating/editing a rule.

    Args:
        st: Streamlit module
        columns: List of available column names

    Returns:
        Rule object if created, None if cancelled
    """
    st.subheader("Create New Rule")

    rule_name = st.text_input("Rule Name", placeholder="e.g., Age must be 0-150")
    rule_description = st.text_area(
        "Description", placeholder="Describe what this rule checks"
    )

    if not columns:
        st.warning("No columns available. Load a dataset first.")
        return None

    selected_column = st.selectbox(
        "Column", options=columns, help="Select column to apply rule to"
    )

    rule_type = st.selectbox(
        "Rule Type",
        options=["range", "regex", "enum"],
        help="Type of rule to create",
    )

    rule_params: dict[str, object] = {}

    if rule_type == "range":
        col1, col2 = st.columns(2)
        with col1:
            min_value = st.number_input(
                "Minimum Value", value=None, help="Minimum allowed value (inclusive)"
            )
            if min_value is not None:
                rule_params["min_value"] = float(min_value)
        with col2:
            max_value = st.number_input(
                "Maximum Value", value=None, help="Maximum allowed value (inclusive)"
            )
            if max_value is not None:
                rule_params["max_value"] = float(max_value)

        if min_value is None and max_value is None:
            st.warning("Please specify at least one of min or max value")

    elif rule_type == "regex":
        pattern = st.text_input(
            "Regex Pattern",
            placeholder="^[A-Z][a-z]+$",
            help="Regular expression pattern",
        )
        if pattern:
            rule_params["pattern"] = pattern
        else:
            st.warning("Please provide a regex pattern")

    elif rule_type == "enum":
        allowed_values_str = st.text_area(
            "Allowed Values (one per line)",
            placeholder="value1\nvalue2\nvalue3",
            help="List of allowed values, one per line",
        )
        if allowed_values_str:
            allowed_values = [
                v.strip() for v in allowed_values_str.split("\n") if v.strip()
            ]
            if allowed_values:
                rule_params["allowed_values"] = allowed_values
            else:
                st.warning(
                    "Please provide at least one allowed value (empty lines are ignored)"
                )
        else:
            st.warning("Please provide allowed values")

    create_button = st.button("Create Rule", type="primary")

    if create_button and rule_name and rule_description and selected_column:
        if rule_type == "range" and (
            rule_params.get("min_value") is not None
            or rule_params.get("max_value") is not None
        ):
            return Rule(
                name=rule_name,
                description=rule_description,
                rule_type="range",
                column=selected_column,
                parameters=rule_params,
                enabled=True,
            )
        elif rule_type == "regex" and rule_params.get("pattern"):
            return Rule(
                name=rule_name,
                description=rule_description,
                rule_type="regex",
                column=selected_column,
                parameters=rule_params,
                enabled=True,
            )
        elif rule_type == "enum" and rule_params.get("allowed_values"):
            return Rule(
                name=rule_name,
                description=rule_description,
                rule_type="enum",
                column=selected_column,
                parameters=rule_params,
                enabled=True,
            )
        else:
            st.error("Please fill in all required fields for the selected rule type")

    return None


def render_rule_list(st: object, ruleset: RuleSet, df: object) -> RuleSet:
    """Render UI for displaying and managing rules.

    Args:
        st: Streamlit module
        ruleset: RuleSet to display
        df: DataFrame being inspected (for getting column names)

    Returns:
        Updated RuleSet
    """
    st.subheader("Rules")

    if not ruleset.rules:
        st.info("No rules defined. Create a rule to get started.")
        return ruleset

    for idx, rule in enumerate(ruleset.rules):
        with st.expander(
            f"{'✅' if rule.enabled else '❌'} {rule.name}", expanded=False
        ):
            st.write(f"**Description:** {rule.description}")
            st.write(f"**Type:** {rule.rule_type}")
            if rule.column:
                st.write(f"**Column:** {rule.column}")
            if rule.parameters:
                st.write("**Parameters:**")
                st.json(rule.parameters)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete", key=f"delete_{idx}"):
                    ruleset.remove_rule(rule.name)
                    # Note: rerun() would be called here in actual Streamlit app
            with col2:
                new_enabled = st.checkbox(
                    "Enabled", value=rule.enabled, key=f"enable_{idx}"
                )
                if new_enabled != rule.enabled:
                    rule.enabled = new_enabled

    return ruleset


def create_rule_executor(rule: Rule) -> RangeRule | RegexRule | EnumRule | None:
    """Create an executor instance from a Rule model.

    Args:
        rule: Rule model to convert

    Returns:
        Rule executor instance or None if rule type is unsupported
    """
    if not rule.enabled:
        return None

    if rule.rule_type == "range":
        return RangeRule(
            name=rule.name,
            description=rule.description,
            column=rule.column or "",  # Should always have column for range rules
            min_value=rule.parameters.get("min_value"),
            max_value=rule.parameters.get("max_value"),
        )
    elif rule.rule_type == "regex":
        pattern = rule.parameters.get("pattern")
        if not pattern:
            return None
        return RegexRule(
            name=rule.name,
            description=rule.description,
            column=rule.column or "",
            pattern=str(pattern),
        )
    elif rule.rule_type == "enum":
        allowed_values = rule.parameters.get("allowed_values")
        if not allowed_values or not isinstance(allowed_values, list):
            return None
        return EnumRule(
            name=rule.name,
            description=rule.description,
            column=rule.column or "",
            allowed_values=[str(v) for v in allowed_values],
        )

    return None


def execute_ruleset(st: object | None, ruleset: RuleSet, df: object) -> list:
    """Execute all enabled rules in a ruleset and return findings.

    Args:
        st: Streamlit module (optional, for error reporting in UI)
        ruleset: RuleSet to execute
        df: DataFrame to check

    Returns:
        List of GhostFinding objects
    """
    from lavendertown.detectors.rule_based import RuleBasedDetector
    from lavendertown.models import GhostFinding

    all_findings: list[GhostFinding] = []

    for rule in ruleset.rules:
        executor = create_rule_executor(rule)
        if executor:
            detector = RuleBasedDetector(executor)
            try:
                findings = detector.detect(df)
                all_findings.extend(findings)
            except Exception as e:
                # Log error but continue
                if st is not None:
                    st.warning(f"Error executing rule '{rule.name}': {e}")
                else:
                    # In CLI context, log the error
                    logger.error(
                        "Error executing rule '%s': %s",
                        rule.name,
                        str(e),
                        exc_info=True,
                    )

    return all_findings


def render_rule_management(st: object, df: object) -> RuleSet:
    """Main rule management UI component.

    Args:
        st: Streamlit module
        df: DataFrame being inspected

    Returns:
        Current RuleSet from session state
    """
    # Get or create ruleset in session state
    if "ruleset" not in st.session_state:
        st.session_state["ruleset"] = RuleSet(
            name="default", description="Default rule set"
        )

    ruleset: RuleSet = st.session_state["ruleset"]

    # Get column names
    backend = _detect_backend(df)
    if backend == "pandas":
        columns = list(df.columns)  # type: ignore[attr-defined]
    else:
        columns = list(df.schema.keys())  # type: ignore[attr-defined]

    # Rule editor section
    with st.expander("➕ Create Rule", expanded=False):
        new_rule = render_rule_editor(st, columns)
        if new_rule:
            ruleset.add_rule(new_rule)
            st.success(f"Rule '{new_rule.name}' created!")
            st.session_state["ruleset"] = ruleset
            # Note: rerun() would be called here in actual Streamlit app, but we'll skip it for now

    # Rule list section
    updated_ruleset = render_rule_list(st, ruleset, df)
    st.session_state["ruleset"] = updated_ruleset

    # Export/Import section
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Rules"):
            ruleset_json = ruleset_to_json(ruleset)
            st.download_button(
                label="📥 Download Rules JSON",
                data=ruleset_json,
                file_name="rules.json",
                mime="application/json",
            )
    with col2:
        uploaded_file = st.file_uploader(
            "Import Rules", type=["json"], help="Upload a rules JSON file"
        )
        if uploaded_file:
            try:
                ruleset_json = uploaded_file.read().decode("utf-8")
                imported_ruleset = ruleset_from_json(ruleset_json)
                st.session_state["ruleset"] = imported_ruleset
                st.success("Rules imported successfully!")
                # Note: rerun() would be called here in actual Streamlit app
            except Exception as e:
                st.error(f"Error importing rules: {e}")

    return st.session_state["ruleset"]


def _detect_backend(df: object) -> str:
    """Detect DataFrame backend (helper function)."""
    from lavendertown.detectors.base import detect_dataframe_backend

    return detect_dataframe_backend(df)
