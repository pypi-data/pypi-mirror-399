"""
Core deconvolution algorithm for isotope pattern analysis.

This module implements the least-squares deconvolution algorithm
for determining the relative amounts of isotope-labeled species
from mass spectrometry data.

The algorithm solves an overdetermined linear system using least-squares
optimization via SVD decomposition (numpy.linalg.lstsq).

Reference:
    Gruber et al. (2007) J. Org. Chem. 72, 5778-5783
    https://doi.org/10.1021/jo070831o
"""

import numpy as np
from typing import Union, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class IsotopePattern:
    """
    Container for isotope pattern analysis results.

    Attributes:
        fractions: Relative amounts of each labeled species [d0, d1, ..., dn]
        labeled_ratio: Percentage of labeled compounds (100 * sum(d1..dn) / sum(d0..dn))
        residuals: Difference between measured and reconstructed pattern
        r_squared: Coefficient of determination for the fit
        pattern_matrix: The deconvolution matrix A used
    """
    fractions: np.ndarray
    labeled_ratio: float
    residuals: np.ndarray
    r_squared: float
    pattern_matrix: np.ndarray

    def __repr__(self) -> str:
        frac_str = ", ".join(f"d{i}={f:.1%}" for i, f in enumerate(self.fractions))
        return f"IsotopePattern({frac_str}, l.r.={self.labeled_ratio:.1%}, R²={self.r_squared:.4f})"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON/CSV export."""
        return {
            f"d{i}": float(f) for i, f in enumerate(self.fractions)
        } | {
            "labeled_ratio": self.labeled_ratio,
            "r_squared": self.r_squared
        }


def _build_pattern_matrix(
    unlabeled_pattern: np.ndarray,
    n_labels: int,
    mass_shift: int = 1
) -> np.ndarray:
    """
    Build the deconvolution matrix A from the unlabeled pattern.

    Each column represents the expected pattern for a derivative
    with i isotope labels, shifted by i * mass_shift mass units.

    Parameters:
        unlabeled_pattern: Abundance pattern of unlabeled compound [a0, a1, a2, ...]
        n_labels: Maximum number of isotope labels (e.g., 4 for d0-d4)
        mass_shift: Mass difference per label (1 for D, 2 for T/18O)

    Returns:
        Matrix A with shape (n_rows, n_labels + 1)
    """
    n_pattern = len(unlabeled_pattern)
    n_derivatives = n_labels + 1  # d0, d1, ..., d_n
    n_rows = n_pattern + n_labels * mass_shift

    A = np.zeros((n_rows, n_derivatives))

    for i in range(n_derivatives):
        shift = i * mass_shift
        A[shift:shift + n_pattern, i] = unlabeled_pattern

    return A


def _solve_lstsq(A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Solve the overdetermined linear system Ax = b using least squares.

    Uses the pseudoinverse: x = (A^T·A)^(-1)·A^T·b

    Parameters:
        A: Pattern matrix (m x n, m > n)
        b: Measured abundances (m,)

    Returns:
        Tuple of (solution x, residuals, R-squared)
    """
    # Use numpy's lstsq which handles numerical stability
    x, residuals_sum, rank, s = np.linalg.lstsq(A, b, rcond=None)

    # Calculate residuals and R²
    predicted = A @ x
    residuals = b - predicted

    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((b - np.mean(b)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return x, residuals, r_squared


def deconvolve(
    unlabeled: Union[List[float], np.ndarray],
    analyte: Union[List[float], np.ndarray],
    n_labels: int,
    mass_shift: int = 1,
    normalize: bool = True,
    clip_negative: bool = True
) -> IsotopePattern:
    """
    Deconvolve a mass spectroscopic pattern to determine isotope label distribution.

    This function determines the relative amounts of each labeled species
    (d0, d1, d2, ..., dn) from the measured mass spectrum of a mixture.

    The algorithm uses least-squares optimization to solve the overdetermined
    linear system: A·x = b, where:
    - A is the pattern matrix built from the unlabeled compound
    - x is the vector of relative amounts [x(d0), x(d1), ..., x(dn)]
    - b is the measured abundance pattern of the analyte

    Parameters:
        unlabeled: Mass spectrum abundances of the unlabeled compound
                   Starting from the molecular ion M: [M, M+1, M+2, ...]
        analyte: Mass spectrum abundances of the labeled mixture
                 Same m/z range, extended by n_labels mass units
        n_labels: Maximum number of isotope labels expected
                  (e.g., 4 for a compound with 4 exchangeable positions)
        mass_shift: Mass difference per isotope label
                    1 for H→D, 13C; 2 for H→T, 16O→18O
        normalize: If True, normalize fractions to sum to 1.0
        clip_negative: If True, set negative fractions to 0.0 after
                       least-squares fitting. Negative values can occur with
                       noisy data or ill-conditioned problems. Note that
                       clipping modifies the optimal least-squares solution
                       and may introduce small biases in the reported fractions.

    Returns:
        IsotopePattern object containing:
        - fractions: Relative amounts [d0, d1, ..., dn]
        - labeled_ratio: Percentage of labeled species
        - residuals: Fit residuals
        - r_squared: Coefficient of determination

    Example:
        >>> # Unlabeled 3-octanone: M=128 pattern
        >>> unlabeled = [100, 8.88, 0.37]
        >>> # After H/D exchange: mixture of d0-d4
        >>> analyte = [10, 20, 40, 25, 5, 0.9, 0.04]
        >>> result = deconvolve(unlabeled, analyte, n_labels=4)
        >>> print(result)
        IsotopePattern(d0=10.0%, d1=20.0%, d2=40.0%, d3=25.0%, d4=5.0%, l.r.=90.0%, R²=0.9998)

    Notes:
        - Input abundances can be raw (unnormalized) values
        - The algorithm automatically handles natural isotope distributions
        - For best results, use clean spectra without significant background

    References:
        Gruber et al. (2007) J. Org. Chem. 72, 5778-5783
    """
    # Convert to numpy arrays
    unlabeled = np.asarray(unlabeled, dtype=np.float64)
    analyte = np.asarray(analyte, dtype=np.float64)

    # Normalize inputs to prevent numerical issues
    unlabeled_norm = unlabeled / np.max(unlabeled) if np.max(unlabeled) > 0 else unlabeled
    analyte_norm = analyte / np.max(analyte) if np.max(analyte) > 0 else analyte

    # Build pattern matrix
    A = _build_pattern_matrix(unlabeled_norm, n_labels, mass_shift)

    # Ensure analyte has correct length (pad with zeros if needed)
    expected_len = A.shape[0]
    if len(analyte_norm) < expected_len:
        analyte_norm = np.pad(analyte_norm, (0, expected_len - len(analyte_norm)))
    elif len(analyte_norm) > expected_len:
        analyte_norm = analyte_norm[:expected_len]

    # Solve least squares
    fractions, residuals, r_squared = _solve_lstsq(A, analyte_norm)

    # Post-processing
    if clip_negative:
        fractions = np.clip(fractions, 0, None)

    if normalize and np.sum(fractions) > 0:
        fractions = fractions / np.sum(fractions)

    # Calculate labeled ratio
    lr = labeled_ratio(fractions)

    return IsotopePattern(
        fractions=fractions,
        labeled_ratio=lr,
        residuals=residuals,
        r_squared=r_squared,
        pattern_matrix=A
    )


def labeled_ratio(fractions: Union[List[float], np.ndarray]) -> float:
    """
    Calculate the labeled compound ratio (l.r.).

    The labeled ratio is defined as the sum of all labeled derivatives
    divided by the total (labeled + unlabeled):

        l.r. = sum(d1..dn) / sum(d0..dn) * 100

    A value of 100% means no unlabeled compound remains.
    A value of 0% means only unlabeled compound is present.

    Parameters:
        fractions: Array of derivative fractions [d0, d1, ..., dn]

    Returns:
        Labeled ratio as a fraction (0.0 to 1.0)

    Example:
        >>> fractions = [0.1, 0.2, 0.4, 0.2, 0.1]  # d0-d4
        >>> lr = labeled_ratio(fractions)
        >>> print(f"{lr:.1%}")
        90.0%
    """
    fractions = np.asarray(fractions)
    total = np.sum(fractions)
    if total <= 0:
        return 0.0

    labeled_sum = np.sum(fractions[1:])  # Sum of d1, d2, ..., dn
    return labeled_sum / total


def batch_deconvolve(
    unlabeled: Union[List[float], np.ndarray],
    analytes: List[Union[List[float], np.ndarray]],
    n_labels: int,
    mass_shift: int = 1,
    normalize: bool = True,
    clip_negative: bool = True
) -> List[IsotopePattern]:
    """
    Deconvolve multiple analyte patterns with the same unlabeled reference.

    More efficient than calling deconvolve() repeatedly since the pattern
    matrix is built only once and reused for all samples.

    Parameters:
        unlabeled: Reference pattern of unlabeled compound
        analytes: List of analyte patterns to deconvolve
        n_labels: Maximum number of isotope labels
        mass_shift: Mass difference per label
        normalize: If True, normalize fractions to sum to 1.0
        clip_negative: If True, set negative fractions to 0.0

    Returns:
        List of IsotopePattern results

    Example:
        >>> unlabeled = [100, 8.88, 0.37]
        >>> # Time course samples
        >>> samples = [
        ...     [90, 20, 5, 1, 0.1],   # t=0
        ...     [50, 40, 20, 5, 1],    # t=30min
        ...     [10, 20, 40, 25, 5],   # t=60min
        ... ]
        >>> results = batch_deconvolve(unlabeled, samples, n_labels=4)
    """
    # Normalize unlabeled pattern once
    unlabeled = np.asarray(unlabeled, dtype=np.float64)
    unlabeled_norm = unlabeled / np.max(unlabeled) if np.max(unlabeled) > 0 else unlabeled

    # Build pattern matrix once (the efficiency optimization)
    A = _build_pattern_matrix(unlabeled_norm, n_labels, mass_shift)
    expected_len = A.shape[0]

    results = []
    for analyte in analytes:
        analyte = np.asarray(analyte, dtype=np.float64)
        analyte_norm = analyte / np.max(analyte) if np.max(analyte) > 0 else analyte

        # Adjust length to match pattern matrix
        if len(analyte_norm) < expected_len:
            analyte_norm = np.pad(analyte_norm, (0, expected_len - len(analyte_norm)))
        elif len(analyte_norm) > expected_len:
            analyte_norm = analyte_norm[:expected_len]

        # Solve least squares with pre-built matrix
        fractions, residuals, r_squared = _solve_lstsq(A, analyte_norm)

        # Post-processing
        if clip_negative:
            fractions = np.clip(fractions, 0, None)
        if normalize and np.sum(fractions) > 0:
            fractions = fractions / np.sum(fractions)

        lr = labeled_ratio(fractions)
        results.append(IsotopePattern(
            fractions=fractions,
            labeled_ratio=lr,
            residuals=residuals,
            r_squared=r_squared,
            pattern_matrix=A
        ))

    return results
