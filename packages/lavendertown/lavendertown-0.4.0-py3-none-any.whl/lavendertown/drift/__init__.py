"""Dataset comparison and drift detection for LavenderTown.

This module provides functionality for comparing datasets and detecting
schema drift, distribution shifts, and other changes between datasets.
"""

from __future__ import annotations

from lavendertown.drift.compare import compare_datasets

__all__ = ["compare_datasets"]
