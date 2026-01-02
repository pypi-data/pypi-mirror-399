"""
Tests for IsoPat I/O utilities.
"""

import pytest
import tempfile
from pathlib import Path
import numpy as np

from isopat.io import read_ms_pattern, write_results, format_results_table
from isopat.core import IsotopePattern


class TestReadMsPattern:
    """Tests for reading MS patterns from files."""

    def test_read_csv(self, tmp_path):
        """Test reading CSV format."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("128,100\n129,8.88\n130,0.37\n")

        mz, intensity = read_ms_pattern(csv_file)

        assert len(mz) == 3
        assert mz[0] == 128
        assert intensity[0] == 100
        assert intensity[1] == pytest.approx(8.88)

    def test_read_tsv(self, tmp_path):
        """Test reading TSV format."""
        tsv_file = tmp_path / "test.tsv"
        tsv_file.write_text("128\t100\n129\t8.88\n130\t0.37\n")

        mz, intensity = read_ms_pattern(tsv_file)

        assert len(mz) == 3
        assert mz[0] == 128

    def test_read_with_header(self, tmp_path):
        """Test reading file with header row."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("m/z,intensity\n128,100\n129,8.88\n")

        mz, intensity = read_ms_pattern(csv_file)

        assert len(mz) == 2
        assert mz[0] == 128

    def test_read_m_range(self, tmp_path):
        """Test extracting specific m/z range."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("127,10\n128,100\n129,8.88\n130,0.37\n131,5\n")

        mz, intensity = read_ms_pattern(csv_file, m_start=128, m_end=130)

        assert len(mz) == 3
        assert mz[0] == 128
        assert mz[-1] == 130

    def test_read_m_start_only(self, tmp_path):
        """Test extracting with only m_start."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("127,10\n128,100\n129,8.88\n")

        mz, intensity = read_ms_pattern(csv_file, m_start=128)

        assert len(mz) == 2
        assert mz[0] == 128

    def test_auto_format_detection(self, tmp_path):
        """Test automatic format detection from file extension."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("128,100\n129,50\n")

        mz, intensity = read_ms_pattern(csv_file, format="auto")

        assert len(mz) == 2


class TestWriteResults:
    """Tests for writing deconvolution results."""

    def test_write_csv(self, tmp_path):
        """Test writing CSV output."""
        result = IsotopePattern(
            fractions=np.array([0.1, 0.9]),
            labeled_ratio=0.9,
            residuals=np.zeros(3),
            r_squared=0.999,
            pattern_matrix=np.eye(2)
        )

        out_file = tmp_path / "results.csv"
        write_results(result, out_file)

        assert out_file.exists()
        content = out_file.read_text()
        assert "d0" in content
        assert "d1" in content
        assert "labeled_ratio" in content
        assert "r_squared" in content

    def test_write_multiple_results(self, tmp_path):
        """Test writing multiple results with sample names."""
        results = [
            IsotopePattern(
                fractions=np.array([0.8, 0.2]),
                labeled_ratio=0.2,
                residuals=np.zeros(3),
                r_squared=0.998,
                pattern_matrix=np.eye(2)
            ),
            IsotopePattern(
                fractions=np.array([0.3, 0.7]),
                labeled_ratio=0.7,
                residuals=np.zeros(3),
                r_squared=0.999,
                pattern_matrix=np.eye(2)
            ),
        ]

        out_file = tmp_path / "results.csv"
        write_results(results, out_file, sample_names=["t0", "t60"])

        content = out_file.read_text()
        assert "t0" in content
        assert "t60" in content

    def test_write_json(self, tmp_path):
        """Test writing JSON output."""
        import json

        result = IsotopePattern(
            fractions=np.array([0.5, 0.5]),
            labeled_ratio=0.5,
            residuals=np.zeros(3),
            r_squared=0.995,
            pattern_matrix=np.eye(2)
        )

        out_file = tmp_path / "results.json"
        write_results(result, out_file, format="json")

        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert "isopat_version" in data
        assert "results" in data

    def test_write_tsv(self, tmp_path):
        """Test writing TSV output."""
        result = IsotopePattern(
            fractions=np.array([0.6, 0.4]),
            labeled_ratio=0.4,
            residuals=np.zeros(3),
            r_squared=0.997,
            pattern_matrix=np.eye(2)
        )

        out_file = tmp_path / "results.tsv"
        write_results(result, out_file, format="tsv")

        content = out_file.read_text()
        assert "\t" in content


class TestFormatResultsTable:
    """Tests for ASCII table formatting."""

    def test_format_single_result(self):
        """Test formatting a single result."""
        result = IsotopePattern(
            fractions=np.array([0.1, 0.2, 0.7]),
            labeled_ratio=0.9,
            residuals=np.zeros(5),
            r_squared=0.999,
            pattern_matrix=np.eye(3)
        )

        table = format_results_table(result)

        assert "d0" in table
        assert "d1" in table
        assert "d2" in table
        assert "l.r." in table
        assert "R²" in table

    def test_format_multiple_results(self):
        """Test formatting multiple results."""
        results = [
            IsotopePattern(
                fractions=np.array([0.9, 0.1]),
                labeled_ratio=0.1,
                residuals=np.zeros(3),
                r_squared=0.999,
                pattern_matrix=np.eye(2)
            ),
            IsotopePattern(
                fractions=np.array([0.1, 0.9]),
                labeled_ratio=0.9,
                residuals=np.zeros(3),
                r_squared=0.998,
                pattern_matrix=np.eye(2)
            ),
        ]

        table = format_results_table(results, sample_names=["before", "after"])

        assert "before" in table
        assert "after" in table

    def test_format_with_precision(self):
        """Test formatting with different precision."""
        result = IsotopePattern(
            fractions=np.array([0.333, 0.667]),
            labeled_ratio=0.667,
            residuals=np.zeros(3),
            r_squared=0.999,
            pattern_matrix=np.eye(2)
        )

        table_low = format_results_table(result, precision=0)
        table_high = format_results_table(result, precision=2)

        # Low precision should have fewer decimal places
        assert "33%" in table_low or "67%" in table_low
        # High precision should have more decimal places
        assert "33.30%" in table_high or "66.70%" in table_high
