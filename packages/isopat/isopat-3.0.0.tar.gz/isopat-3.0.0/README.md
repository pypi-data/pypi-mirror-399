# IsoPat 3.0: A Python Package for Isotope Pattern Deconvolution in Mass Spectrometry

[![PyPI version](https://badge.fury.io/py/isopat.svg)](https://badge.fury.io/py/isopat)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Christian C. Gruber**<sup>1,2</sup>, **Wolfgang Kroutil**<sup>3</sup>

1. Innophore GmbH, Graz, Austria
2. Institute of Molecular Bioscience, University of Graz, Austria
3. Institute of Chemistry, University of Graz, Austria

## Abstract

Isotope labeling is a fundamental technique in chemistry and biochemistry for investigating molecular structures, reaction mechanisms, and metabolic pathways. The accurate determination of isotope incorporation from mass spectrometry data requires deconvolution of overlapping isotope patterns—a non-trivial task when multiple labeled species are present. **IsoPat** provides a Python implementation of a least-squares deconvolution algorithm that determines the relative amounts of each isotope-labeled species from low-resolution mass spectrometry data. The package features minimal dependencies (NumPy only), a clean documented API, command-line interface for batch processing, and comprehensive tests for the core algorithm.

![Figure 1: IsoPat algorithm overview](figures/figure_1.png)

**Figure 1:** IsoPat algorithm overview. (A) Natural isotope distribution of unlabeled 3-octanone. (B) Pattern matrix A showing shifted patterns for each derivative d₀–d₄. (C) Comparison of measured and fitted analyte patterns with R² = 0.9999. (D) Deconvolution results showing relative fractions of each labeled species.

## Installation

```bash
pip install isopat
```

## Quick Start

```python
from isopat import deconvolve

# Unlabeled compound pattern (M, M+1, M+2 from natural isotopes)
unlabeled = [100, 8.88, 0.37]

# Measured pattern after H/D exchange (mixture of d0-d4)
analyte = [10, 20, 40, 25, 5, 0.9, 0.04]

# Deconvolve to get relative amounts of each species
result = deconvolve(unlabeled, analyte, n_labels=4)

print(result)
# IsotopePattern(d0=10.0%, d1=20.0%, d2=40.0%, d3=25.0%, d4=5.0%, l.r.=90.0%, R²=0.9998)
```

## Command Line Interface

```bash
# Single pattern deconvolution
isopat deconvolve -u "100,8.88,0.37" -a "10,20,40,25,5,0.9,0.04" -n 4

# Batch processing
isopat batch -u reference.csv -a samples.csv -n 4 -o results.csv
```

## Algorithm

IsoPat solves an overdetermined linear system using least-squares optimization:

**A·x = b**

Where:
- **A** = Pattern matrix built from the unlabeled compound
- **x** = Relative amounts of each labeled species [d₀, d₁, ..., dₙ]
- **b** = Measured abundance pattern

The solution minimizes the error using the pseudoinverse:

**x = (AᵀA)⁻¹Aᵀb**

## Features

- **Minimal dependencies**: Only requires NumPy
- **Multiple isotope schemes**: H→D, ¹²C→¹³C, ¹⁶O→¹⁸O, etc.
- **Batch processing**: Efficiently process time-course data
- **Quality metrics**: R² values for fit assessment
- **Flexible I/O**: CSV, TSV, JSON support

## API Reference

### `deconvolve(unlabeled, analyte, n_labels, mass_shift=1)`

Deconvolve a single mass spectrum pattern.

**Parameters:**
- `unlabeled`: Reference pattern of unlabeled compound
- `analyte`: Measured pattern of labeled mixture
- `n_labels`: Maximum number of isotope labels
- `mass_shift`: Mass difference per label (1 for D/¹³C, 2 for T/¹⁸O)

**Returns:** `IsotopePattern` with fractions, labeled_ratio, and R²

### `batch_deconvolve(unlabeled, analytes, n_labels)`

Process multiple patterns efficiently.

### `labeled_ratio(fractions)`

Calculate the labeled compound ratio: `l.r. = Σ(d₁..dₙ) / Σ(d₀..dₙ)`

## Citation

If you use IsoPat in your research, please cite:

```bibtex
@article{gruber2007isopat,
  title={An algorithm for the deconvolution of mass spectroscopic patterns
         in isotope labeling studies},
  author={Gruber, Christian C and Oberdorfer, Gustav and Voss, Constance V
          and Kremsner, Jennifer M and Kappe, C Oliver and Kroutil, Wolfgang},
  journal={The Journal of Organic Chemistry},
  volume={72},
  number={15},
  pages={5778--5783},
  year={2007},
  doi={10.1021/jo070831o}
}

@article{gruber2025isopat3,
  title={IsoPat 3.0: A Python package for isotope pattern deconvolution
         in mass spectrometry},
  author={Gruber, Christian C and Kroutil, Wolfgang},
  journal={Journal of Open Source Software},
  year={2025}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Authors

- **Christian C. Gruber** - Innophore / University of Graz
- **Wolfgang Kroutil** - University of Graz
