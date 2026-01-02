"""Inspector orchestrator - main entry point for LavenderTown."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.detectors.null import NullGhostDetector
from lavendertown.detectors.type import TypeGhostDetector
from lavendertown.detectors.outlier import OutlierGhostDetector
from lavendertown.models import GhostFinding


class Inspector:
    """Main orchestrator for data quality inspection.

    The Inspector coordinates ghost detection, aggregates findings,
    and renders the Streamlit UI.
    """

    def __init__(
        self,
        df: object,
        detectors: list[GhostDetector] | None = None,
    ) -> None:
        """Initialize the Inspector.

        Args:
            df: DataFrame to inspect (Pandas or Polars)
            detectors: Optional list of custom detectors. If None, uses default detectors.
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

        Args:
            show_progress: If True and Streamlit is available, show progress indicators

        Returns:
            List of all GhostFinding objects from all detectors
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
                # In production, you might want proper logging here
                print(f"Error in detector {detector.get_name()}: {e}")

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

        This is the main entry point for the Streamlit application.
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

        Args:
            show_progress: If True, show progress indicators during detection
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

        Args:
            baseline_df: Baseline DataFrame to compare against (Pandas or Polars)
            comparison_type: Type of comparison ("full", "schema_only", "distribution_only")
            distribution_threshold: Percentage threshold for distribution changes

        Returns:
            List of GhostFinding objects with ghost_type="drift"
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
        """Generate a hash for the DataFrame for caching purposes."""

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
        """Render sidebar with summary and filters."""
        from lavendertown.ui.sidebar import render_sidebar

        render_sidebar(st, self.df, findings, self.backend)

    def _render_main(self, st: object, findings: list[GhostFinding]) -> None:
        """Render main content area."""
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
