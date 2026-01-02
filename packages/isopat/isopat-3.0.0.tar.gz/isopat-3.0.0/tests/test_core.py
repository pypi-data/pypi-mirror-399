"""
Tests for IsoPat core functionality.
"""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_almost_equal

from isopat import deconvolve, labeled_ratio, IsotopePattern
from isopat.core import _build_pattern_matrix, batch_deconvolve


class TestBuildPatternMatrix:
    """Tests for pattern matrix construction."""

    def test_simple_pattern(self):
        """Test matrix construction for a simple pattern."""
        unlabeled = np.array([100, 10, 1])
        A = _build_pattern_matrix(unlabeled, n_labels=2, mass_shift=1)

        expected_shape = (5, 3)  # 3 + 2 rows, 3 columns
        assert A.shape == expected_shape

        # Check first column (d0)
        assert_array_almost_equal(A[:3, 0], unlabeled)
        assert A[3, 0] == 0
        assert A[4, 0] == 0

        # Check second column (d1) - shifted by 1
        assert A[0, 1] == 0
        assert_array_almost_equal(A[1:4, 1], unlabeled)
        assert A[4, 1] == 0

    def test_mass_shift_2(self):
        """Test matrix construction with mass_shift=2 (e.g., 18O)."""
        unlabeled = np.array([100, 10])
        A = _build_pattern_matrix(unlabeled, n_labels=1, mass_shift=2)

        expected_shape = (4, 2)  # 2 + 1*2 rows, 2 columns
        assert A.shape == expected_shape

        # d0 at positions 0,1
        assert A[0, 0] == 100
        assert A[1, 0] == 10

        # d1 at positions 2,3
        assert A[2, 1] == 100
        assert A[3, 1] == 10


class TestDeconvolve:
    """Tests for the main deconvolution function."""

    def test_pure_unlabeled(self):
        """Test deconvolution of purely unlabeled sample."""
        unlabeled = np.array([100, 8.88, 0.37])
        analyte = unlabeled.copy()

        result = deconvolve(unlabeled, analyte, n_labels=2)

        # Should be 100% d0
        assert result.fractions[0] > 0.95
        assert np.sum(result.fractions[1:]) < 0.05
        assert result.labeled_ratio < 0.05
        assert result.r_squared > 0.99

    def test_pure_d1(self):
        """Test deconvolution of purely d1 sample."""
        unlabeled = np.array([100, 10, 1])
        # d1 pattern is shifted by 1
        analyte = np.array([0, 100, 10, 1])

        result = deconvolve(unlabeled, analyte, n_labels=2)

        # Should be ~100% d1
        assert result.fractions[0] < 0.05
        assert result.fractions[1] > 0.95
        assert result.labeled_ratio > 0.95

    def test_known_mixture(self):
        """Test deconvolution of a known mixture."""
        unlabeled = np.array([100, 10, 1])

        # Create a 50:50 mixture of d0 and d1
        d0_contrib = 0.5 * unlabeled
        d1_contrib = 0.5 * np.array([0, 100, 10, 1])
        analyte = np.zeros(4)
        analyte[:3] += d0_contrib
        analyte[1:] += 0.5 * unlabeled

        result = deconvolve(unlabeled, analyte, n_labels=2)

        # Should be approximately 50:50
        assert_almost_equal(result.fractions[0], 0.5, decimal=1)
        assert_almost_equal(result.fractions[1], 0.5, decimal=1)
        assert_almost_equal(result.labeled_ratio, 0.5, decimal=1)

    def test_normalization(self):
        """Test that fractions sum to 1.0."""
        unlabeled = np.array([100, 8.88, 0.37])
        analyte = np.array([10, 20, 40, 25, 5, 0.9, 0.04])

        result = deconvolve(unlabeled, analyte, n_labels=4)

        assert_almost_equal(np.sum(result.fractions), 1.0, decimal=6)

    def test_different_scales(self):
        """Test that different input scales give same result."""
        unlabeled = np.array([100, 8.88, 0.37])
        analyte = np.array([10, 20, 40, 25, 5, 0.9, 0.04])

        result1 = deconvolve(unlabeled, analyte, n_labels=4)
        result2 = deconvolve(unlabeled * 10, analyte * 100, n_labels=4)

        assert_array_almost_equal(result1.fractions, result2.fractions, decimal=4)

    def test_r_squared_quality(self):
        """Test R² indicates good fit for valid data."""
        unlabeled = np.array([100, 8.88, 0.37])

        # Create perfect d2 pattern
        analyte = np.array([0, 0, 100, 8.88, 0.37])

        result = deconvolve(unlabeled, analyte, n_labels=4)

        assert result.r_squared > 0.99


class TestLabeledRatio:
    """Tests for labeled ratio calculation."""

    def test_all_unlabeled(self):
        """Test l.r. = 0% for pure unlabeled."""
        fractions = np.array([1.0, 0.0, 0.0])
        lr = labeled_ratio(fractions)
        assert_almost_equal(lr, 0.0)

    def test_all_labeled(self):
        """Test l.r. = 100% for no d0."""
        fractions = np.array([0.0, 0.5, 0.5])
        lr = labeled_ratio(fractions)
        assert_almost_equal(lr, 1.0)

    def test_half_labeled(self):
        """Test l.r. = 50% for equal d0 and labeled."""
        fractions = np.array([0.5, 0.25, 0.25])
        lr = labeled_ratio(fractions)
        assert_almost_equal(lr, 0.5)

    def test_empty_fractions(self):
        """Test handling of zero fractions."""
        fractions = np.array([0.0, 0.0, 0.0])
        lr = labeled_ratio(fractions)
        assert lr == 0.0


class TestBatchDeconvolve:
    """Tests for batch processing."""

    def test_batch_multiple_samples(self):
        """Test batch processing of multiple samples."""
        unlabeled = np.array([100, 8.88, 0.37])
        analytes = [
            np.array([100, 8.88, 0.37, 0, 0]),  # Pure d0
            np.array([0, 100, 8.88, 0.37, 0]),  # Pure d1
            np.array([50, 54, 4.4, 0.18, 0]),   # ~50:50 mix
        ]

        results = batch_deconvolve(unlabeled, analytes, n_labels=2)

        assert len(results) == 3
        assert results[0].fractions[0] > 0.9  # Mostly d0
        assert results[1].fractions[1] > 0.9  # Mostly d1


class TestIsotopePattern:
    """Tests for IsotopePattern dataclass."""

    def test_repr(self):
        """Test string representation."""
        result = IsotopePattern(
            fractions=np.array([0.1, 0.2, 0.7]),
            labeled_ratio=0.9,
            residuals=np.zeros(5),
            r_squared=0.999,
            pattern_matrix=np.eye(3)
        )

        repr_str = repr(result)
        assert "d0=10.0%" in repr_str
        assert "l.r.=90.0%" in repr_str
        assert "R²=0.9990" in repr_str

    def test_to_dict(self):
        """Test dictionary conversion."""
        result = IsotopePattern(
            fractions=np.array([0.1, 0.2, 0.7]),
            labeled_ratio=0.9,
            residuals=np.zeros(5),
            r_squared=0.999,
            pattern_matrix=np.eye(3)
        )

        d = result.to_dict()
        assert d["d0"] == pytest.approx(0.1)
        assert d["d1"] == pytest.approx(0.2)
        assert d["d2"] == pytest.approx(0.7)
        assert d["labeled_ratio"] == pytest.approx(0.9)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_short_analyte_padded(self):
        """Test that short analyte patterns are padded."""
        unlabeled = np.array([100, 10, 1])
        analyte = np.array([100, 10])  # Too short

        # Should not raise, pattern is padded
        result = deconvolve(unlabeled, analyte, n_labels=2)
        assert result is not None

    def test_long_analyte_truncated(self):
        """Test that long analyte patterns are truncated."""
        unlabeled = np.array([100, 10, 1])
        analyte = np.array([100, 10, 1, 0.1, 0.01, 0.001, 0.0001])

        result = deconvolve(unlabeled, analyte, n_labels=2)
        assert result is not None

    def test_negative_clipping(self):
        """Test that negative fractions are clipped to zero."""
        unlabeled = np.array([100, 10, 1])
        # Noisy data that might produce negative values
        analyte = np.array([100, 5, 1, 0.5, 0.1])

        result = deconvolve(unlabeled, analyte, n_labels=2, clip_negative=True)

        assert np.all(result.fractions >= 0)


# Regression tests based on paper examples
class TestPaperExamples:
    """Tests based on examples from Gruber et al. (2007)."""

    def test_3octanone_pattern(self):
        """Test with 3-octanone pattern from paper (Figure 1)."""
        # M=128 for 3-octanone
        # Natural abundance pattern approximation
        unlabeled = np.array([100, 8.88, 0.37])

        # Simulated d4 enriched sample (from paper discussion)
        # After 200 min at 180°C: ~85% d4
        analyte = np.array([2, 3, 5, 10, 85, 7.5, 0.3])

        result = deconvolve(unlabeled, analyte, n_labels=4)

        # The d4 fraction should be the highest
        assert np.argmax(result.fractions) == 4
        # Labeled ratio should be very high
        assert result.labeled_ratio > 0.95
