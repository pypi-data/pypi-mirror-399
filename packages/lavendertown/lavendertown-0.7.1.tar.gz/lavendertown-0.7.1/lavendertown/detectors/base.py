"""Base class for ghost detectors.

This module provides the abstract base class for all ghost detectors and
utilities for detecting DataFrame backends (Pandas vs Polars). Detectors
are stateless, UI-agnostic modules that analyze DataFrames and return
normalized GhostFinding objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from lavendertown.models import GhostFinding


def detect_dataframe_backend(df: object) -> str:
    """Detect whether a DataFrame is Pandas or Polars.

    Examines the DataFrame object's attributes to determine which backend
    library it belongs to. This allows LavenderTown to use the appropriate
    API for each backend.

    Args:
        df: DataFrame object to inspect. Should be a pandas.DataFrame or
            polars.DataFrame instance.

    Returns:
        String indicating the backend: "pandas" or "polars".

    Raises:
        ValueError: If the DataFrame type cannot be determined (not Pandas
            or Polars). This typically means an unsupported DataFrame type
            was passed.

    Example:
        Detect backend before performing operations::

            backend = detect_dataframe_backend(df)
            if backend == "pandas":
                # Use pandas API
                result = df[column].isna().sum()
            else:
                # Use polars API
                result = df[column].null_count()
    """
    # Check for Pandas
    if hasattr(df, "to_dict") and hasattr(df, "iloc") and hasattr(df, "dtypes"):
        return "pandas"

    # Check for Polars
    if hasattr(df, "to_pandas") and hasattr(df, "select") and hasattr(df, "schema"):
        return "polars"

    raise ValueError(
        f"Unsupported DataFrame type: {type(df)}. "
        "Expected pandas.DataFrame or polars.DataFrame"
    )


class GhostDetector(ABC):
    """Abstract base class for all ghost detectors.

    Detectors are stateless and UI-agnostic modules that analyze DataFrames
    and return normalized GhostFinding objects. They implement a single
    ``detect()`` method that takes a DataFrame (Pandas or Polars) and
    returns a list of findings.

    Detectors should be designed to work with both Pandas and Polars
    DataFrames by detecting the backend and using the appropriate API.

    Subclasses must implement the ``detect()`` method. The ``get_name()``
    method provides a default implementation that returns the class name,
    but can be overridden for custom naming.

    Example:
        Implement a custom detector::

            from lavendertown.detectors.base import GhostDetector
            from lavendertown.models import GhostFinding
            from lavendertown.detectors.base import detect_dataframe_backend

            class CustomDetector(GhostDetector):
                def detect(self, df):
                    backend = detect_dataframe_backend(df)
                    findings = []
                    # Custom detection logic here
                    return findings
    """

    @abstractmethod
    def detect(self, df: object) -> list[GhostFinding]:
        """Detect ghosts in the given DataFrame.

        This is the main method that subclasses must implement. It should
        analyze the DataFrame for specific types of data quality issues
        and return a list of findings.

        Args:
            df: DataFrame to analyze. Can be a pandas.DataFrame or
                polars.DataFrame. The detector should use
                ``detect_dataframe_backend()`` to determine which API to use.

        Returns:
            List of GhostFinding objects representing all detected issues
            of this detector's type. Can be an empty list if no issues
            are found.

        Note:
            Detectors should handle both Pandas and Polars DataFrames.
            Use ``detect_dataframe_backend()`` to determine which API to use.
        """
        pass

    def get_name(self) -> str:
        """Get the name of this detector.

        Returns the human-readable name of the detector. By default, this
        returns the class name, but subclasses can override this method
        to provide a more descriptive name.

        Returns:
            String name of the detector. Used in UI displays and progress
            indicators. Defaults to the class name (e.g., "NullGhostDetector").
        """
        return self.__class__.__name__
