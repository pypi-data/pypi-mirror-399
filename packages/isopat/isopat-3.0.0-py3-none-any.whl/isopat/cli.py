"""
Command-line interface for IsoPat.

Usage:
    isopat deconvolve --unlabeled PATTERN --analyte PATTERN --labels N
    isopat batch --unlabeled FILE --analytes FILE --labels N --output FILE

Examples:
    # Single deconvolution from command line
    isopat deconvolve --unlabeled "100,8.88,0.37" --analyte "10,20,40,25,5,0.9,0.04" --labels 4

    # Batch processing from files
    isopat batch --unlabeled reference.csv --analytes samples.csv --labels 4 --output results.csv
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List

import numpy as np

from . import __version__
from .core import deconvolve, batch_deconvolve
from .io import read_ms_pattern, write_results, format_results_table


def parse_pattern(pattern_str: str) -> np.ndarray:
    """Parse comma-separated pattern string to numpy array."""
    values = [float(x.strip()) for x in pattern_str.split(",")]
    return np.array(values)


def cmd_deconvolve(args: argparse.Namespace) -> int:
    """Execute single deconvolution."""
    try:
        unlabeled = parse_pattern(args.unlabeled)
        analyte = parse_pattern(args.analyte)

        result = deconvolve(
            unlabeled,
            analyte,
            n_labels=args.labels,
            mass_shift=args.mass_shift
        )

        # Output
        if args.json:
            import json
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"\nIsoPat {__version__} - Deconvolution Result")
            print("=" * 50)
            print(f"Unlabeled pattern: {unlabeled}")
            print(f"Analyte pattern:   {analyte}")
            print(f"Max labels:        {args.labels}")
            print("-" * 50)
            print("\nFractions:")
            for i, f in enumerate(result.fractions):
                print(f"  d{i}: {f:7.1%}")
            print(f"\nLabeled ratio: {result.labeled_ratio:.1%}")
            print(f"R² (fit):      {result.r_squared:.4f}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_batch(args: argparse.Namespace) -> int:
    """Execute batch deconvolution from files."""
    try:
        # Read unlabeled pattern
        if args.unlabeled.endswith((".csv", ".tsv", ".txt")):
            _, unlabeled = read_ms_pattern(args.unlabeled)
        else:
            unlabeled = parse_pattern(args.unlabeled)

        # Read analytes file (one pattern per row)
        analytes = []
        sample_names = []

        with open(args.analytes, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            raise ValueError("Empty analytes file")

        # Filter out comment rows and empty rows first
        rows = [row for row in rows if row and not row[0].strip().startswith("#")]

        if not rows:
            raise ValueError("No data rows found in analytes file")

        # Determine if first column contains sample names by checking
        # the header row. If first cell is a known header keyword, assume
        # sample names are present. This avoids the bug where numeric
        # sample IDs (e.g., "1", "2") were misinterpreted as data.
        has_sample_column = False
        has_header = False
        header_keywords = {"sample", "name", "id", "sample_name", "sample_id"}

        first_row = rows[0]
        if first_row and first_row[0].strip().lower() in header_keywords:
            has_header = True
            has_sample_column = True
        elif first_row and not first_row[0].strip():
            # Empty first cell in header indicates sample column
            has_header = True
            has_sample_column = True

        # If --sample-names flag is set, always expect sample names
        if getattr(args, 'sample_names', False):
            has_sample_column = True

        # Process rows (skip header if detected)
        data_rows = rows[1:] if has_header else rows
        row_idx = 0

        for row in data_rows:
            # Skip empty rows
            if not row:
                continue

            # Filter out empty cells
            row = [cell.strip() for cell in row if cell.strip()]
            if len(row) < 2:
                continue

            if has_sample_column:
                sample_names.append(row[0])
                pattern_data = row[1:]
            else:
                sample_names.append(f"sample_{row_idx + 1}")
                pattern_data = row

            try:
                pattern = [float(x) for x in pattern_data]
                analytes.append(np.array(pattern))
                row_idx += 1
            except ValueError as e:
                raise ValueError(
                    f"Cannot parse row {row_idx + 1}: non-numeric value in pattern data"
                ) from e

        # Deconvolve
        results = batch_deconvolve(
            unlabeled,
            analytes,
            n_labels=args.labels,
            mass_shift=args.mass_shift
        )

        # Output
        if args.output:
            write_results(results, args.output, sample_names=sample_names)
            print(f"Results written to: {args.output}")
        else:
            print(format_results_table(results, sample_names=sample_names))

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: List[str] = None) -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="isopat",
        description="IsoPat - Isotope Pattern Deconvolution for Mass Spectrometry"
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Deconvolve command
    deconv_parser = subparsers.add_parser(
        "deconvolve",
        help="Deconvolve a single pattern"
    )
    deconv_parser.add_argument(
        "--unlabeled", "-u", required=True,
        help="Comma-separated unlabeled pattern (e.g., '100,8.88,0.37')"
    )
    deconv_parser.add_argument(
        "--analyte", "-a", required=True,
        help="Comma-separated analyte pattern"
    )
    deconv_parser.add_argument(
        "--labels", "-n", type=int, required=True,
        help="Maximum number of isotope labels"
    )
    deconv_parser.add_argument(
        "--mass-shift", "-m", type=int, default=1,
        help="Mass shift per label (default: 1 for D, 13C)"
    )
    deconv_parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON"
    )
    deconv_parser.set_defaults(func=cmd_deconvolve)

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch deconvolve multiple patterns"
    )
    batch_parser.add_argument(
        "--unlabeled", "-u", required=True,
        help="Unlabeled pattern (comma-separated or file path)"
    )
    batch_parser.add_argument(
        "--analytes", "-a", required=True,
        help="File with analyte patterns (one per row)"
    )
    batch_parser.add_argument(
        "--labels", "-n", type=int, required=True,
        help="Maximum number of isotope labels"
    )
    batch_parser.add_argument(
        "--mass-shift", "-m", type=int, default=1,
        help="Mass shift per label (default: 1)"
    )
    batch_parser.add_argument(
        "--output", "-o",
        help="Output file (CSV/TSV/JSON based on extension)"
    )
    batch_parser.add_argument(
        "--sample-names", "-s", action="store_true",
        dest="sample_names",
        help="First column contains sample names (use when names are numeric)"
    )
    batch_parser.set_defaults(func=cmd_batch)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
