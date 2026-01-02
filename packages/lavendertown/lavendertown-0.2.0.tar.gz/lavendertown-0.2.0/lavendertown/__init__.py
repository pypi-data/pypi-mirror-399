"""LavenderTown - A Streamlit-first data quality inspection framework.

LavenderTown is a Python package for detecting and visualizing "data ghosts":
type inconsistencies, nulls, invalid values, schema drift, and anomalies
in tabular datasets. It provides an intuitive, interactive Streamlit interface
for data quality analysis and supports both Pandas and Polars DataFrames.

Example:
    Basic usage with Streamlit::

        import streamlit as st
        from lavendertown import Inspector
        import pandas as pd

        df = pd.read_csv("data.csv")
        inspector = Inspector(df)
        inspector.render()

    Programmatic usage without UI::

        from lavendertown import Inspector
        import pandas as pd

        df = pd.read_csv("data.csv")
        inspector = Inspector(df)
        findings = inspector.detect()

        for finding in findings:
            print(f"{finding.column}: {finding.description}")
"""

__version__ = "0.2.0"

from lavendertown.inspector import Inspector
from lavendertown.models import GhostFinding
from lavendertown.detectors.base import GhostDetector

__all__ = ["Inspector", "GhostFinding", "GhostDetector"]
