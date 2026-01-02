"""
Tests for IsoPat command-line interface.
"""

import pytest
import sys
from pathlib import Path
from io import StringIO

from isopat.cli import main, parse_pattern


class TestParsePattern:
    """Tests for pattern string parsing."""

    def test_parse_simple_pattern(self):
        """Test parsing a simple comma-separated pattern."""
        result = parse_pattern("100,8.88,0.37")

        assert len(result) == 3
        assert result[0] == 100
        assert result[1] == pytest.approx(8.88)
        assert result[2] == pytest.approx(0.37)

    def test_parse_with_spaces(self):
        """Test parsing pattern with spaces."""
        result = parse_pattern("100, 8.88, 0.37")

        assert len(result) == 3
        assert result[0] == 100

    def test_parse_single_value(self):
        """Test parsing single value pattern."""
        result = parse_pattern("100")

        assert len(result) == 1
        assert result[0] == 100


class TestDeconvolveCommand:
    """Tests for the deconvolve subcommand."""

    def test_basic_deconvolve(self, capsys):
        """Test basic deconvolution via CLI."""
        args = [
            "deconvolve",
            "-u", "100,8.88,0.37",
            "-a", "10,20,40,25,5,0.9,0.04",
            "-n", "4"
        ]

        result = main(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "IsoPat" in captured.out
        assert "d0:" in captured.out
        assert "d4:" in captured.out
        assert "Labeled ratio:" in captured.out

    def test_deconvolve_json_output(self, capsys):
        """Test JSON output format."""
        args = [
            "deconvolve",
            "-u", "100,8.88,0.37",
            "-a", "10,20,40,25,5,0.9,0.04",
            "-n", "4",
            "--json"
        ]

        result = main(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "{" in captured.out
        assert "labeled_ratio" in captured.out

    def test_deconvolve_mass_shift(self, capsys):
        """Test deconvolution with custom mass shift."""
        args = [
            "deconvolve",
            "-u", "100,5.5,0.3",
            "-a", "80,4.4,20,1.1,0.06",
            "-n", "1",
            "-m", "2"  # 18O labeling
        ]

        result = main(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "d0:" in captured.out
        assert "d1:" in captured.out


class TestBatchCommand:
    """Tests for the batch subcommand."""

    def test_batch_with_header(self, tmp_path, capsys):
        """Test batch processing with header row."""
        # Create analytes file with header
        analytes_file = tmp_path / "samples.csv"
        analytes_file.write_text(
            "sample,M,M+1,M+2,M+3,M+4,M+5,M+6\n"
            "t0,95,10,1,0.1,0.01,0.9,0.04\n"
            "t60,10,20,40,25,5,0.9,0.04\n"
        )

        args = [
            "batch",
            "-u", "100,8.88,0.37",
            "-a", str(analytes_file),
            "-n", "4"
        ]

        result = main(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "t0" in captured.out
        assert "t60" in captured.out

    def test_batch_numeric_only(self, tmp_path, capsys):
        """Test batch processing with numeric-only data (no sample names)."""
        analytes_file = tmp_path / "samples.csv"
        analytes_file.write_text(
            "95,10,1,0.1,0.01,0.9,0.04\n"
            "10,20,40,25,5,0.9,0.04\n"
        )

        args = [
            "batch",
            "-u", "100,8.88,0.37",
            "-a", str(analytes_file),
            "-n", "4"
        ]

        result = main(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "sample_1" in captured.out
        assert "sample_2" in captured.out

    def test_batch_with_sample_names_flag(self, tmp_path, capsys):
        """Test batch processing with --sample-names flag for numeric IDs."""
        # This tests the fix for the numeric sample ID bug
        analytes_file = tmp_path / "samples.csv"
        analytes_file.write_text(
            "1,95,10,1,0.1,0.01,0.9,0.04\n"
            "2,10,20,40,25,5,0.9,0.04\n"
        )

        args = [
            "batch",
            "-u", "100,8.88,0.37",
            "-a", str(analytes_file),
            "-n", "4",
            "--sample-names"  # Explicitly indicate first column is sample name
        ]

        result = main(args)

        assert result == 0
        captured = capsys.readouterr()
        # With --sample-names, "1" and "2" should be treated as sample names
        assert "1" in captured.out or "2" in captured.out

    def test_batch_output_file(self, tmp_path):
        """Test batch processing with output to file."""
        analytes_file = tmp_path / "samples.csv"
        analytes_file.write_text(
            "sample,M,M+1,M+2,M+3,M+4\n"
            "test1,100,8.88,0.37,0,0\n"
        )

        output_file = tmp_path / "results.csv"

        args = [
            "batch",
            "-u", "100,8.88,0.37",
            "-a", str(analytes_file),
            "-n", "2",
            "-o", str(output_file)
        ]

        result = main(args)

        assert result == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "test1" in content

    def test_batch_empty_file_error(self, tmp_path, capsys):
        """Test error handling for empty file."""
        analytes_file = tmp_path / "empty.csv"
        analytes_file.write_text("")

        args = [
            "batch",
            "-u", "100,8.88,0.37",
            "-a", str(analytes_file),
            "-n", "4"
        ]

        result = main(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err or "Empty" in captured.err

    def test_batch_skip_comments(self, tmp_path, capsys):
        """Test that comment lines are skipped."""
        analytes_file = tmp_path / "samples.csv"
        analytes_file.write_text(
            "# This is a comment\n"
            "sample,M,M+1,M+2,M+3,M+4\n"
            "test1,100,8.88,0.37,0,0\n"
        )

        args = [
            "batch",
            "-u", "100,8.88,0.37",
            "-a", str(analytes_file),
            "-n", "2"
        ]

        result = main(args)

        assert result == 0


class TestMainHelp:
    """Tests for CLI help and version."""

    def test_no_command_shows_help(self, capsys):
        """Test that running without command shows help."""
        result = main([])

        assert result == 0
        captured = capsys.readouterr()
        assert "IsoPat" in captured.out or "usage" in captured.out.lower()

    def test_version_flag(self, capsys):
        """Test --version flag."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])

        # argparse exits with 0 for --version
        assert exc_info.value.code == 0
