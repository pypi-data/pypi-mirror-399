"""Parquet exporter for ghost findings.

This module provides functions to export findings to Parquet format using PyArrow.
Parquet is an efficient columnar storage format suitable for large datasets and
analytics workloads.
"""

from __future__ import annotations

import json
from typing import Any

try:
    import pyarrow as pa
    import pyarrow.parquet as pq

    _PYARROW_AVAILABLE = True
except ImportError:
    _PYARROW_AVAILABLE = False
    pa = None  # type: ignore[assignment,misc]
    pq = None  # type: ignore[assignment,misc]

from lavendertown.models import GhostFinding


def export_findings_to_parquet(
    findings: list[GhostFinding],
    filepath: str,
    compression: str = "snappy",
) -> None:
    """Export findings to Parquet format.

    Exports findings to a Parquet file using PyArrow. This format is efficient
    for large datasets and analytics workloads.

    Args:
        findings: List of GhostFinding objects to export
        filepath: Path to output Parquet file
        compression: Compression codec to use. Options: "snappy" (default),
            "gzip", "brotli", "zstd", "lz4", "uncompressed"

    Raises:
        ImportError: If PyArrow is not installed. Install with:
            pip install lavendertown[parquet]
        ValueError: If compression codec is invalid
    """
    if not _PYARROW_AVAILABLE:
        raise ImportError(
            "PyArrow is required for Parquet export. Install with: pip install lavendertown[parquet]"
        )

    valid_compressions = {"snappy", "gzip", "brotli", "zstd", "lz4", "uncompressed"}
    if compression not in valid_compressions:
        raise ValueError(
            f"Invalid compression: {compression}. Must be one of {valid_compressions}"
        )

    # Convert findings to PyArrow Table
    table = _findings_to_arrow_table(findings)

    # Write to Parquet file
    pq.write_table(
        table,
        filepath,
        compression=compression,
        use_dictionary=True,  # Enable dictionary encoding for better compression
    )


def export_findings_to_parquet_bytes(
    findings: list[GhostFinding],
    compression: str = "snappy",
) -> bytes:
    """Export findings to Parquet format as bytes.

    Exports findings to Parquet format in memory, returning the bytes.
    Useful for in-memory operations or streaming.

    Args:
        findings: List of GhostFinding objects to export
        compression: Compression codec to use. Options: "snappy" (default),
            "gzip", "brotli", "zstd", "lz4", "uncompressed"

    Returns:
        Bytes containing the Parquet file data

    Raises:
        ImportError: If PyArrow is not installed. Install with:
            pip install lavendertown[parquet]
        ValueError: If compression codec is invalid
    """
    if not _PYARROW_AVAILABLE:
        raise ImportError(
            "PyArrow is required for Parquet export. Install with: pip install lavendertown[parquet]"
        )

    valid_compressions = {"snappy", "gzip", "brotli", "zstd", "lz4", "uncompressed"}
    if compression not in valid_compressions:
        raise ValueError(
            f"Invalid compression: {compression}. Must be one of {valid_compressions}"
        )

    # Convert findings to PyArrow Table
    table = _findings_to_arrow_table(findings)

    # Create in-memory buffer
    sink = pa.BufferOutputStream()

    # Write to buffer
    table_any: Any = table
    with pq.ParquetWriter(  # type: ignore[call-overload]
        sink,
        table_any.schema,  # type: ignore[attr-defined]
        compression=compression,
        use_dictionary=True,
    ) as writer:
        writer.write_table(table_any)  # type: ignore[call-overload]

    # Get bytes
    buffer_value: Any = sink.getvalue()
    return bytes(buffer_value.to_pybytes())  # type: ignore[attr-defined]


def _findings_to_arrow_table(findings: list[GhostFinding]) -> Any:
    """Convert findings to PyArrow Table.

    Args:
        findings: List of GhostFinding objects

    Returns:
        PyArrow Table containing the findings data
    """
    if not _PYARROW_AVAILABLE:
        raise ImportError("PyArrow is required for Parquet export")

    # Prepare data arrays
    ghost_types: list[str] = []
    columns: list[str] = []
    severities: list[str] = []
    descriptions: list[str] = []
    row_counts: list[int] = []
    row_indices_list: list[str] = []  # JSON-serialized list of indices
    metadata_list: list[str] = []  # JSON-serialized metadata

    for finding in findings:
        ghost_types.append(finding.ghost_type)
        columns.append(finding.column)
        severities.append(finding.severity)
        descriptions.append(finding.description)

        # Row count
        row_count = len(finding.row_indices) if finding.row_indices else 0
        row_counts.append(row_count)

        # Serialize row_indices to JSON string
        row_indices_json = (
            json.dumps(finding.row_indices, default=str)
            if finding.row_indices is not None
            else ""
        )
        row_indices_list.append(row_indices_json)

        # Serialize metadata to JSON string
        metadata_json = (
            json.dumps(finding.metadata, default=str) if finding.metadata else "{}"
        )
        metadata_list.append(metadata_json)

    # Create PyArrow arrays
    arrays = [
        pa.array(ghost_types, type=pa.string()),
        pa.array(columns, type=pa.string()),
        pa.array(severities, type=pa.string()),
        pa.array(descriptions, type=pa.string()),
        pa.array(row_counts, type=pa.int64()),
        pa.array(row_indices_list, type=pa.string()),
        pa.array(metadata_list, type=pa.string()),
    ]

    # Create schema
    schema = pa.schema(
        [
            ("ghost_type", pa.string()),
            ("column", pa.string()),
            ("severity", pa.string()),
            ("description", pa.string()),
            ("row_count", pa.int64()),
            ("row_indices", pa.string()),
            ("metadata", pa.string()),
        ]
    )

    # Create table
    table = pa.Table.from_arrays(arrays, schema=schema)

    return table


def read_findings_from_parquet(filepath: str) -> list[GhostFinding]:
    """Read findings from a Parquet file.

    Reads findings that were previously exported to Parquet format.
    This is useful for reading exported findings back into LavenderTown.

    Args:
        filepath: Path to the Parquet file

    Returns:
        List of GhostFinding objects

    Raises:
        ImportError: If PyArrow is not installed
        FileNotFoundError: If the file doesn't exist
    """
    if not _PYARROW_AVAILABLE:
        raise ImportError(
            "PyArrow is required for Parquet import. Install with: pip install lavendertown[parquet]"
        )

    # Read Parquet file
    table = pq.read_table(filepath)

    # Convert to pandas for easier processing
    df = table.to_pandas()

    # Convert back to findings
    findings: list[GhostFinding] = []
    for _, row in df.iterrows():
        # Deserialize row_indices
        row_indices = None
        if row["row_indices"]:
            row_indices = json.loads(row["row_indices"])

        # Deserialize metadata
        metadata = {}
        if row["metadata"]:
            metadata = json.loads(row["metadata"])

        finding = GhostFinding(
            ghost_type=row["ghost_type"],
            column=row["column"],
            severity=row["severity"],
            description=row["description"],
            row_indices=row_indices,
            metadata=metadata,
        )
        findings.append(finding)

    return findings
