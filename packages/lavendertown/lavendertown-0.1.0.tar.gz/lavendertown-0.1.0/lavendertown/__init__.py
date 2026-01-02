"""LavenderTown - A Streamlit-first data quality inspection framework."""

__version__ = "0.1.0"

from lavendertown.inspector import Inspector
from lavendertown.models import GhostFinding
from lavendertown.detectors.base import GhostDetector

__all__ = ["Inspector", "GhostFinding", "GhostDetector"]
