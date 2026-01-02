"""Inspector orchestrator - main entry point for LavenderTown.

This module provides the Inspector class, which orchestrates data quality
detection, aggregates findings from multiple detectors, and renders the
Streamlit UI. The Inspector supports both Pandas and Polars DataFrames
and can detect drift between datasets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.detectors.null import NullGhostDetector
from lavendertown.detectors.type import TypeGhostDetector
from lavendertown.detectors.outlier import OutlierGhostDetector
from lavendertown.logging_config import get_logger
from lavendertown.models import GhostFinding

logger = get_logger(__name__)


class Inspector:
    """Main orchestrator for data quality inspection.

    The Inspector coordinates ghost detection across multiple detectors,
    aggregates findings, and renders the Streamlit UI. It automatically
    detects whether the input DataFrame is Pandas or Polars and uses
    the appropriate backend for operations.

    By default, the Inspector uses three built-in detectors:
    - NullGhostDetector: Detects excessive null values
    - TypeGhostDetector: Identifies type inconsistencies
    - OutlierGhostDetector: Finds statistical outliers using IQR method

    Custom detectors can be provided to extend functionality.

    Attributes:
        df: The DataFrame being inspected (Pandas or Polars).
        backend: Detected backend type ("pandas" or "polars").
        detectors: List of ghost detectors to run.
        _findings: Cached list of findings from detection (None until first detection).
        _baseline_df: Optional baseline DataFrame for drift comparison.

    Example:
        Basic usage::

            from lavendertown import Inspector
            import pandas as pd

            df = pd.read_csv("data.csv")
            inspector = Inspector(df)

            # Detect issues programmatically
            findings = inspector.detect()
            for finding in findings:
                print(f"{finding.column}: {finding.description}")

            # Or render Streamlit UI
            inspector.render()

        With custom detectors::

            from lavendertown import Inspector, GhostDetector
            import pandas as pd

            class CustomDetector(GhostDetector):
                def detect(self, df):
                    # Custom detection logic
                    return []

            inspector = Inspector(df, detectors=[CustomDetector()])
            findings = inspector.detect()
    """

    def __init__(
        self,
        df: object,
        detectors: list[GhostDetector] | None = None,
    ) -> None:
        """Initialize the Inspector.

        Args:
            df: DataFrame to inspect. Can be a pandas.DataFrame or polars.DataFrame.
                The backend will be automatically detected.
            detectors: Optional list of custom GhostDetector instances to use.
                If None, uses the default set of detectors (NullGhostDetector,
                TypeGhostDetector, OutlierGhostDetector).

        Raises:
            ValueError: If the DataFrame type cannot be detected (not Pandas or Polars).
        """
        self.df = df
        self.backend = detect_dataframe_backend(df)

        # Register detectors
        if detectors is None:
            self.detectors = [
                NullGhostDetector(),
                TypeGhostDetector(),
                OutlierGhostDetector(),
            ]
        else:
            self.detectors = detectors

        # Findings will be cached after first detection
        self._findings: list[GhostFinding] | None = None

        # Baseline DataFrame for drift comparison (optional)
        self._baseline_df: object | None = None

    def detect(self, show_progress: bool = False) -> list[GhostFinding]:
        """Run all detectors and aggregate findings.

        Executes all registered detectors on the DataFrame and returns a
        combined list of all findings. Results are cached after the first
        call to avoid redundant computation.

        Args:
            show_progress: If True and Streamlit is available, displays
                progress indicators during detection. Defaults to False.

        Returns:
            List of GhostFinding objects representing all detected data
            quality issues. Each finding contains information about the
            ghost type, affected column, severity, description, and
            optionally the row indices of affected rows.

        Note:
            If a detector raises an exception, it is logged but detection
            continues with other detectors. The error will not stop the
            overall detection process.
        """
        if self._findings is not None:
            return self._findings

        all_findings: list[GhostFinding] = []

        # Show progress if requested and Streamlit is available
        progress_bar = None
        if show_progress:
            try:
                import streamlit as st  # type: ignore[import-untyped,unused-ignore]

                progress_bar = st.progress(0.0)
                status_text = st.empty()
            except ImportError:
                progress_bar = None

        num_detectors = len(self.detectors)
        for idx, detector in enumerate(self.detectors):
            if progress_bar is not None:
                try:
                    import streamlit as st  # type: ignore[import-untyped,unused-ignore]

                    status_text.text(
                        f"Running {detector.get_name()}... ({idx + 1}/{num_detectors})"
                    )
                    progress_bar.progress((idx + 0.5) / num_detectors)
                except ImportError:
                    pass

            try:
                findings = detector.detect(self.df)
                all_findings.extend(findings)
            except Exception as e:
                # Log error but continue with other detectors
                logger.error(
                    "Error in detector '%s': %s",
                    detector.get_name(),
                    str(e),
                    exc_info=True,
                )

        if progress_bar is not None:
            try:
                import streamlit as st  # type: ignore[import-untyped,unused-ignore]

                progress_bar.progress(1.0)
                status_text.text("Analysis complete!")
            except ImportError:
                pass

        self._findings = all_findings
        return all_findings

    def render(self) -> None:
        """Render the Streamlit UI.

        This is the main entry point for the Streamlit application. It renders
        the complete data quality inspection interface including:
        - Sidebar with dataset summary and filters
        - Overview metrics and summary statistics
        - Interactive charts for visualizing findings
        - Filterable table of problematic rows
        - Export functionality for findings
        - Rule management interface

        The UI includes Streamlit caching to optimize performance on repeated
        runs with the same data.

        Raises:
            ImportError: If Streamlit is not installed. Install it with
                ``pip install streamlit``.

        Note:
            This method must be called within a Streamlit app context.
            It will not work in a regular Python script or notebook without
            Streamlit running.

        Example:
            Create a file ``app.py``::

                import streamlit as st
                from lavendertown import Inspector
                import pandas as pd

                df = pd.read_csv("data.csv")
                inspector = Inspector(df)
                inspector.render()

            Then run: ``streamlit run app.py``
        """
        try:
            import streamlit as st  # type: ignore[import-untyped,unused-ignore]
        except ImportError:
            raise ImportError(
                "Streamlit is required to use Inspector.render(). "
                "Install it with: pip install streamlit"
            )

        # Run detection (with caching and progress)
        findings = self._get_cached_findings(show_progress=True)

        # Render UI components
        self._render_sidebar(st, findings)  # type: ignore[arg-type,unused-ignore]
        self._render_main(st, findings)  # type: ignore[arg-type,unused-ignore]

    def _get_cached_findings(self, show_progress: bool = False) -> list[GhostFinding]:
        """Get findings with Streamlit caching.

        Retrieves findings using Streamlit's caching mechanism to avoid
        redundant computation. Also includes any findings from custom rules
        stored in session state.

        Args:
            show_progress: If True, displays progress indicators during
                detection. Defaults to False.

        Returns:
            List of GhostFinding objects combining detector findings and
            rule-based findings.
        """
        try:
            import streamlit as st
        except ImportError:
            return self.detect(show_progress=show_progress)

        # Check for rules in session state and execute them
        rule_findings: list[GhostFinding] = []
        if "ruleset" in st.session_state:
            from lavendertown.ui.rules import execute_ruleset

            try:
                ruleset = st.session_state["ruleset"]
                rule_findings = execute_ruleset(st, ruleset, self.df)  # type: ignore[arg-type]
            except Exception:
                pass  # Silently fail if rules can't be executed

        # Create a cache key based on DataFrame hash and detector names
        @st.cache_data  # type: ignore[attr-defined]
        def _detect_ghosts(df_hash: str, detector_names: tuple[str, ...]) -> list[dict]:  # type: ignore[assignment]
            # Re-run detection (progress is handled outside cache)
            findings = self.detect(show_progress=False)
            # Convert to dict for caching (dataclasses aren't directly cacheable)
            return [f.to_dict() for f in findings]

        # Generate hash for DataFrame
        df_hash = self._hash_dataframe()
        detector_names = tuple(d.get_name() for d in self.detectors)

        # Show progress if requested (before caching check)
        if show_progress:
            with st.spinner("Analyzing data quality..."):
                findings_dicts = _detect_ghosts(df_hash, detector_names)
        else:
            findings_dicts = _detect_ghosts(df_hash, detector_names)

        # Convert back to GhostFinding objects and combine with rule findings
        detector_findings = [GhostFinding.from_dict(f) for f in findings_dicts]
        return detector_findings + rule_findings

    def compare_with_baseline(
        self,
        baseline_df: object,
        comparison_type: str = "full",
        distribution_threshold: float = 10.0,
    ) -> list[GhostFinding]:
        """Compare current DataFrame with a baseline DataFrame for drift detection.

        Detects changes between the baseline and current datasets, including:
        - Schema changes (new/removed columns, type changes, nullability changes)
        - Distribution changes (null percentage shifts, numeric range shifts,
          cardinality changes)

        Args:
            baseline_df: Baseline DataFrame to compare against. Can be a
                pandas.DataFrame or polars.DataFrame. Must be compatible
                with the current DataFrame's backend.
            comparison_type: Type of comparison to perform. Options:
                - "full": Both schema and distribution checks (default)
                - "schema_only": Only schema-related drift detection
                - "distribution_only": Only distribution-related drift detection
            distribution_threshold: Percentage threshold for considering a
                distribution change significant. Default is 10.0 (10%).
                Changes below this threshold are ignored.

        Returns:
            List of GhostFinding objects with ghost_type="drift". Also includes
            regular detection findings from the current DataFrame. Each drift
            finding contains metadata about the type of change detected.

        Example:
            Detect drift between two dataset versions::

                import pandas as pd
                from lavendertown import Inspector

                baseline = pd.read_csv("baseline.csv")
                current = pd.read_csv("current.csv")

                inspector = Inspector(current)
                findings = inspector.compare_with_baseline(
                    baseline_df=baseline,
                    comparison_type="full",
                    distribution_threshold=15.0
                )

                drift_findings = [f for f in findings if f.ghost_type == "drift"]
                for finding in drift_findings:
                    print(f"{finding.column}: {finding.description}")
        """
        from lavendertown.drift.compare import compare_datasets

        drift_findings = compare_datasets(
            baseline_df=baseline_df,
            current_df=self.df,
            comparison_type=comparison_type,
            distribution_threshold=distribution_threshold,
        )

        # Combine with regular detection findings
        regular_findings = self.detect()
        return regular_findings + drift_findings

    def _hash_dataframe(self) -> str:
        """Generate a hash for the DataFrame for caching purposes.

        Creates a hash representation of the DataFrame to use as a cache key.
        Uses byte-level hashing for Pandas DataFrames and string representation
        for Polars DataFrames.

        Returns:
            String representation of the DataFrame hash.
        """

        if self.backend == "pandas":
            # Use pandas hash
            try:
                return str(hash(self.df.values.tobytes()))  # type: ignore[attr-defined]
            except Exception:
                # Fallback to string representation
                return str(hash(str(self.df)))
        else:
            # For Polars, use string representation
            return str(hash(str(self.df)))

    def _render_sidebar(self, st: object, findings: list[GhostFinding]) -> None:
        """Render sidebar with summary and filters.

        Args:
            st: Streamlit module object.
            findings: List of GhostFinding objects to display in sidebar.
        """
        from lavendertown.ui.sidebar import render_sidebar

        render_sidebar(st, self.df, findings, self.backend)

    def _render_main(self, st: object, findings: list[GhostFinding]) -> None:
        """Render main content area.

        Renders the main UI panels including overview, charts, table,
        export section, and optionally the rules management panel.

        Args:
            st: Streamlit module object.
            findings: List of GhostFinding objects to display.
        """
        from lavendertown.ui.overview import render_overview
        from lavendertown.ui.charts import render_charts
        from lavendertown.ui.table import render_table
        from lavendertown.ui.export import render_export_section
        from lavendertown.ui.rules import render_rule_management

        # Rules panel (if requested)
        if st.session_state.get("show_rules_panel", False):  # type: ignore[attr-defined,index]
            st.header("📋 Rule Management")  # type: ignore[attr-defined]
            render_rule_management(st, self.df)  # type: ignore[arg-type]
            if st.button("Close Rules Panel"):  # type: ignore[attr-defined]
                st.session_state["show_rules_panel"] = False  # type: ignore[attr-defined,index]
                # Note: rerun() would be called here in actual Streamlit app
            st.divider()  # type: ignore[attr-defined]

        # Overview section
        render_overview(st, findings)

        st.divider()  # type: ignore[attr-defined]

        # Charts section
        render_charts(st, self.df, findings, self.backend)

        st.divider()  # type: ignore[attr-defined]

        # Table section
        render_table(st, self.df, findings, self.backend)

        st.divider()  # type: ignore[attr-defined]

        # Export section
        render_export_section(st, findings)
