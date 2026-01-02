"""Base class for ghost detectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from lavendertown.models import GhostFinding


def detect_dataframe_backend(df: object) -> str:
    """Detect whether a DataFrame is Pandas or Polars.

    Args:
        df: DataFrame object to inspect

    Returns:
        "pandas" or "polars"

    Raises:
        ValueError: If DataFrame type cannot be determined
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

    Detectors are stateless and UI-agnostic. They analyze DataFrames
    and return normalized GhostFinding objects.
    """

    @abstractmethod
    def detect(self, df: object) -> list[GhostFinding]:
        """Detect ghosts in the given DataFrame.

        Args:
            df: DataFrame (Pandas or Polars) to analyze

        Returns:
            List of GhostFinding objects representing detected issues
        """
        pass

    def get_name(self) -> str:
        """Get the name of this detector.

        Returns:
            Detector name, defaults to class name
        """
        return self.__class__.__name__
