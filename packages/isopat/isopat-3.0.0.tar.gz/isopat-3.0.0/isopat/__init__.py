"""
IsoPat - Isotope Pattern Deconvolution for Mass Spectrometry
============================================================

A Python tool for deconvolution of mass spectroscopic patterns
in isotope labeling studies using least-squares optimization.

Based on: Gruber et al. (2007) J. Org. Chem. 72, 5778-5783
https://doi.org/10.1021/jo070831o

Authors:
    Christian C. Gruber
    Wolfgang Kroutil

Example:
    >>> from isopat import deconvolve
    >>> unlabeled = [100, 11.1, 0.6]  # M, M+1, M+2 pattern
    >>> analyte = [20, 40, 30, 10]    # mixture pattern
    >>> fractions = deconvolve(unlabeled, analyte, n_labels=3)
    >>> print(fractions)  # [d0, d1, d2, d3] fractions
"""

__version__ = "3.0.0"
__author__ = "Christian C. Gruber, Wolfgang Kroutil"
__email__ = "christian.gruber@innophore.com"

from .core import deconvolve, labeled_ratio, IsotopePattern
from .io import read_ms_pattern, write_results

__all__ = [
    "deconvolve",
    "labeled_ratio",
    "IsotopePattern",
    "read_ms_pattern",
    "write_results",
    "__version__",
]
