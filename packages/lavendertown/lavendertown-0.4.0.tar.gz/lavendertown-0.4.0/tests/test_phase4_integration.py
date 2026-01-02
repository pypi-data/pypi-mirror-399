"""Integration tests for Phase 4 features.

These tests verify that Phase 4 features work together correctly and
integrate properly with existing LavenderTown functionality.
"""

from __future__ import annotations

import pandas as pd
import pytest

from lavendertown import Inspector
from lavendertown.collaboration.api import (
    add_annotation,
    create_shareable_report,
    get_annotations,
)
from lavendertown.collaboration.storage import get_finding_id
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector
from lavendertown.models import GhostFinding
from lavendertown.rules.cross_column import CrossColumnRule
from lavendertown.rules.executors import RangeRule


class TestPhase4Integration:
    """Integration tests for Phase 4 features."""

    def test_inspector_with_timeseries_detector(self):
        """Test Inspector integration with TimeSeriesAnomalyDetector."""
        import pandas as pd

        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        df = pd.DataFrame(
            {
                "timestamp": dates,
                "value": [
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
                    100,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                ],
            }
        )

        detector = TimeSeriesAnomalyDetector(
            datetime_column="timestamp", sensitivity=3.0
        )
        inspector = Inspector(df, detectors=[detector])

        findings = inspector.detect()
        timeseries_findings = [
            f for f in findings if f.ghost_type == "timeseries_anomaly"
        ]
        assert len(timeseries_findings) > 0

    def test_inspector_with_ml_detector(self):
        """Test Inspector integration with MLAnomalyDetector."""
        import importlib.util

        if importlib.util.find_spec("sklearn") is None:
            pytest.skip("scikit-learn not installed")

        df = pd.DataFrame(
            {
                "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
                "col2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            }
        )

        detector = MLAnomalyDetector(algorithm="isolation_forest", contamination=0.1)
        inspector = Inspector(df, detectors=[detector])

        findings = inspector.detect()
        ml_findings = [f for f in findings if f.ghost_type == "ml_anomaly"]
        assert len(ml_findings) > 0

    def test_cross_column_rule_with_ruleset(self):
        """Test cross-column rule integrated with RuleSet."""
        df = pd.DataFrame(
            {
                "price": [100, 200, 150, 300],
                "cost": [50, 150, 200, 250],
            }
        )

        rule = CrossColumnRule(
            name="price_gt_cost",
            description="price must be greater than cost",
            source_columns=["price", "cost"],
            operation="greater_than",
        )

        from lavendertown.detectors.rule_based import RuleBasedDetector

        detector = RuleBasedDetector(rule)
        findings = detector.detect(df)

        assert len(findings) > 0
        assert findings[0].ghost_type == "rule"

    def test_multiple_detectors_together(self):
        """Test multiple Phase 4 detectors working together."""
        import importlib.util

        if importlib.util.find_spec("sklearn") is None:
            pytest.skip("scikit-learn not installed")

        import pandas as pd

        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        df = pd.DataFrame(
            {
                "timestamp": dates,
                "value": [
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
                    100,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                ],
                "value2": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
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
                ],
            }
        )

        timeseries_detector = TimeSeriesAnomalyDetector(datetime_column="timestamp")
        ml_detector = MLAnomalyDetector()

        inspector = Inspector(df, detectors=[timeseries_detector, ml_detector])
        findings = inspector.detect()

        timeseries_findings = [
            f for f in findings if f.ghost_type == "timeseries_anomaly"
        ]
        ml_findings = [f for f in findings if f.ghost_type == "ml_anomaly"]

        assert len(timeseries_findings) > 0 or len(ml_findings) > 0

    def test_collaboration_with_findings(self):
        """Test collaboration features with actual findings."""
        finding = GhostFinding(
            ghost_type="timeseries_anomaly",
            column="value",
            severity="warning",
            description="Time-series anomaly detected",
            metadata={"method": "zscore"},
        )

        # Add annotation
        annotation = add_annotation(
            finding,
            author="Alice",
            comment="This anomaly looks suspicious",
            tags=["review", "urgent"],
            status="reviewed",
        )

        assert annotation.finding_id == get_finding_id(finding)

        # Create report with finding and annotation
        report = create_shareable_report(
            title="Anomaly Report",
            author="Alice",
            findings=[finding],
            annotations=[annotation],
        )

        assert len(report.findings) == 1
        assert len(report.annotations) == 1
        assert report.annotations[0].comment == "This anomaly looks suspicious"

    def test_cross_column_and_single_column_rules_together(self):
        """Test cross-column rules with single-column rules."""
        df = pd.DataFrame(
            {
                "price": [100, 200, 150, 300],
                "cost": [50, 150, 200, 250],
                "quantity": [10, 20, 15, 30],
            }
        )

        # Single-column rule
        range_rule = RangeRule(
            name="price_range",
            description="Price must be positive",
            column="price",
            min_value=0.0,
        )

        # Cross-column rule
        cross_rule = CrossColumnRule(
            name="price_gt_cost",
            description="price must be greater than cost",
            source_columns=["price", "cost"],
            operation="greater_than",
        )

        from lavendertown.detectors.rule_based import RuleBasedDetector

        range_detector = RuleBasedDetector(range_rule)
        cross_detector = RuleBasedDetector(cross_rule)

        range_findings = range_detector.detect(df)
        cross_findings = cross_detector.detect(df)

        # Both should work independently
        assert isinstance(range_findings, list)
        assert isinstance(cross_findings, list)

    def test_report_with_all_finding_types(self):
        """Test report containing all types of findings."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="email",
                severity="warning",
                description="Null finding",
            ),
            GhostFinding(
                ghost_type="timeseries_anomaly",
                column="value",
                severity="info",
                description="Time-series finding",
            ),
            GhostFinding(
                ghost_type="ml_anomaly",
                column="col1, col2",
                severity="warning",
                description="ML finding",
            ),
            GhostFinding(
                ghost_type="rule",
                column="price",
                severity="error",
                description="Rule violation",
            ),
        ]

        report = create_shareable_report(
            title="Comprehensive Report",
            author="Alice",
            findings=findings,
        )

        assert len(report.findings) == 4
        finding_types = {f.ghost_type for f in report.findings}
        assert "null" in finding_types
        assert "timeseries_anomaly" in finding_types
        assert "ml_anomaly" in finding_types
        assert "rule" in finding_types

    def test_annotation_persistence(self):
        """Test that annotations persist across multiple calls."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        # Add annotation
        add_annotation(finding, "Alice", "First comment")

        # Get annotations
        annotations1 = get_annotations(finding)
        assert len(annotations1) > 0

        # Add another annotation
        add_annotation(finding, "Bob", "Second comment")

        # Get annotations again
        annotations2 = get_annotations(finding)
        assert len(annotations2) > len(annotations1)

    def test_finding_id_with_metadata(self):
        """Test finding ID generation with metadata."""
        finding1 = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
            metadata={"key1": "value1"},
        )

        finding2 = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
            metadata={"key2": "value2"},
        )

        # IDs should be same (metadata not used in ID generation)
        id1 = get_finding_id(finding1)
        id2 = get_finding_id(finding2)
        assert id1 == id2
