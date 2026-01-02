"""
Input/Output utilities for IsoPat.

Functions for reading mass spectrometry data from various formats
and writing deconvolution results.
"""

import csv
import json
from pathlib import Path
from typing import Union, List, Tuple, Optional, Dict, Any
import numpy as np

from .core import IsotopePattern


def read_ms_pattern(
    filepath: Union[str, Path],
    format: str = "auto",
    m_start: Optional[int] = None,
    m_end: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Read mass spectrometry pattern from file.

    Supports CSV, TSV, and simple text formats with two columns:
    m/z and abundance.

    Parameters:
        filepath: Path to the input file
        format: File format ("csv", "tsv", "txt", or "auto")
        m_start: Starting m/z to extract (optional)
        m_end: Ending m/z to extract (optional)

    Returns:
        Tuple of (m/z array, abundance array)

    Example:
        >>> mz, abundance = read_ms_pattern("spectrum.csv")
        >>> # Or extract specific range
        >>> mz, abundance = read_ms_pattern("spectrum.csv", m_start=128, m_end=135)
    """
    filepath = Path(filepath)

    # Auto-detect format
    if format == "auto":
        suffix = filepath.suffix.lower()
        if suffix == ".csv":
            format = "csv"
        elif suffix in (".tsv", ".txt"):
            format = "tsv"
        else:
            format = "tsv"  # Default to tab-separated

    delimiter = "," if format == "csv" else "\t"

    mz_values = []
    abundances = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)

        # Skip header if present
        first_row = next(reader)
        try:
            mz_values.append(float(first_row[0]))
            abundances.append(float(first_row[1]))
        except ValueError:
            pass  # Header row, skip it

        for row in reader:
            if len(row) >= 2:
                try:
                    mz = float(row[0])
                    abundance = float(row[1])
                    mz_values.append(mz)
                    abundances.append(abundance)
                except ValueError:
                    continue

    mz_array = np.array(mz_values)
    abundance_array = np.array(abundances)

    # Extract range if specified
    if m_start is not None or m_end is not None:
        mask = np.ones(len(mz_array), dtype=bool)
        if m_start is not None:
            mask &= mz_array >= m_start
        if m_end is not None:
            mask &= mz_array <= m_end

        mz_array = mz_array[mask]
        abundance_array = abundance_array[mask]

    return mz_array, abundance_array


def write_results(
    results: Union[IsotopePattern, List[IsotopePattern]],
    filepath: Union[str, Path],
    format: str = "csv",
    sample_names: Optional[List[str]] = None
) -> None:
    """
    Write deconvolution results to file.

    Parameters:
        results: Single IsotopePattern or list of results
        filepath: Output file path
        format: Output format ("csv", "tsv", or "json")
        sample_names: Optional names for each sample

    Example:
        >>> result = deconvolve(unlabeled, analyte, n_labels=4)
        >>> write_results(result, "results.csv")
        >>>
        >>> # Multiple results with names
        >>> results = batch_deconvolve(unlabeled, samples, n_labels=4)
        >>> write_results(results, "timecourse.csv",
        ...               sample_names=["t0", "t30", "t60"])
    """
    filepath = Path(filepath)

    # Ensure results is a list
    if isinstance(results, IsotopePattern):
        results = [results]

    # Generate sample names if not provided
    if sample_names is None:
        sample_names = [f"sample_{i+1}" for i in range(len(results))]

    if format == "json":
        _write_json(results, filepath, sample_names)
    else:
        delimiter = "," if format == "csv" else "\t"
        _write_csv(results, filepath, delimiter, sample_names)


def _write_csv(
    results: List[IsotopePattern],
    filepath: Path,
    delimiter: str,
    sample_names: List[str]
) -> None:
    """Write results in CSV/TSV format."""
    # Determine max number of labels
    max_labels = max(len(r.fractions) for r in results)

    # Build header
    header = ["sample"]
    header.extend([f"d{i}" for i in range(max_labels)])
    header.extend(["labeled_ratio", "r_squared"])

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(header)

        for name, result in zip(sample_names, results):
            row = [name]
            # Pad fractions if needed
            fractions = list(result.fractions)
            fractions.extend([0.0] * (max_labels - len(fractions)))
            row.extend([f"{f:.6f}" for f in fractions])
            row.append(f"{result.labeled_ratio:.6f}")
            row.append(f"{result.r_squared:.6f}")
            writer.writerow(row)


def _write_json(
    results: List[IsotopePattern],
    filepath: Path,
    sample_names: List[str]
) -> None:
    """Write results in JSON format."""
    data = {
        "isopat_version": "3.0.0",
        "results": {}
    }

    for name, result in zip(sample_names, results):
        data["results"][name] = result.to_dict()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def format_results_table(
    results: Union[IsotopePattern, List[IsotopePattern]],
    sample_names: Optional[List[str]] = None,
    precision: int = 1
) -> str:
    """
    Format results as a readable ASCII table.

    Parameters:
        results: Single result or list of results
        sample_names: Optional names for samples
        precision: Decimal places for percentages

    Returns:
        Formatted table string

    Example:
        >>> print(format_results_table(results, sample_names=["t0", "t30", "t60"]))
        Sample    d0       d1       d2       d3       d4       l.r.    R²
        ──────────────────────────────────────────────────────────────────
        t0       90.0%     8.0%     2.0%     0.0%     0.0%    10.0%   0.999
        t30      50.0%    30.0%    15.0%     4.0%     1.0%    50.0%   0.998
        t60      10.0%    20.0%    40.0%    20.0%    10.0%    90.0%   0.999
    """
    if isinstance(results, IsotopePattern):
        results = [results]

    if sample_names is None:
        sample_names = [f"sample_{i+1}" for i in range(len(results))]

    max_labels = max(len(r.fractions) for r in results)

    # Build header
    lines = []
    header_parts = ["Sample".ljust(10)]
    header_parts.extend([f"d{i}".rjust(8) for i in range(max_labels)])
    header_parts.extend(["l.r.".rjust(8), "R²".rjust(7)])
    lines.append("".join(header_parts))
    lines.append("─" * len(lines[0]))

    # Format each row
    fmt = f"{{:.{precision}%}}"
    for name, result in zip(sample_names, results):
        row_parts = [name.ljust(10)]
        for i in range(max_labels):
            if i < len(result.fractions):
                row_parts.append(fmt.format(result.fractions[i]).rjust(8))
            else:
                row_parts.append("—".rjust(8))
        row_parts.append(fmt.format(result.labeled_ratio).rjust(8))
        row_parts.append(f"{result.r_squared:.3f}".rjust(7))
        lines.append("".join(row_parts))

    return "\n".join(lines)
