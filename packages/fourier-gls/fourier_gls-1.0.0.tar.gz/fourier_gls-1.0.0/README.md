# Fourier GLS Unit Root Tests

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/fourier-gls.svg)](https://badge.fury.io/py/fourier-gls)

A Python implementation of the Flexible Fourier Form and Local Generalised Least Squares De-trended Unit Root Tests.

## Reference

**Rodrigues, P. M. M and Taylor, A. M. R. (2012)**  
*"The Flexible Fourier Form and Local Generalised Least Squares De-trended Unit Root Tests."*  
Oxford Bulletin of Economics and Statistics, 74(5), 736-759.

## Features

- **Fourier GLS Test**: Local GLS de-trended unit root test with Fourier approximation for unknown structural breaks
- **Fourier DF Test**: OLS de-trended Dickey-Fuller test with Fourier terms (Enders & Lee, 2009)
- **Fourier LM Test**: First-difference de-trended LM test with Fourier terms (Schmidt & Phillips, 1992)
- **F-Test for Linearity**: Test significance of Fourier terms
- **Data-Driven Frequency Selection**: Automatic selection using Davies (1987) procedure
- **Critical Values**: Complete tables from the original paper (Tables 1-3)
- **Publication-Ready Output**: Formatted results suitable for academic papers

## Installation

```bash
pip install fourier-gls
```

Or install from source:

```bash
git clone https://github.com/merwanroudane/fouriergls.git
cd fouriergls
pip install -e .
```

## Quick Start

```python
import numpy as np
from fourier_gls import fourier_gls

# Generate sample data (unit root with structural break)
np.random.seed(42)
T = 200
t = np.arange(1, T + 1)
y = np.cumsum(np.random.randn(T)) + 5 * np.sin(2 * np.pi * t / T)

# Run Fourier GLS test
result = fourier_gls(y, model=2)  # model=2 includes constant and trend
```

Output:
```
================================================================================
                    Fourier GLS Unit Root Test Results
================================================================================
Reference: Rodrigues & Taylor (2012), Oxford Bulletin of Economics and Statistics

Model:               Constant + Trend
Sample Size:         200
Selected Frequency:  k = 1
Selected Lags:       2

--------------------------------------------------------------------------------
Test Statistic:      -3.2456
--------------------------------------------------------------------------------

Critical Values:
    1%:   -4.5930
    5%:   -4.0410
    10%:  -3.7490

--------------------------------------------------------------------------------
Conclusion (5% level): Fail to reject H0: No evidence against unit root at 5% level
================================================================================
```

## API Reference

### Main Functions

#### `fourier_gls(y, model=2, pmax=8, fmax=5, ic=3, verbose=True)`

Performs the Fourier GLS unit root test with automatic frequency selection.

**Parameters:**
- `y` : array-like - Time series data
- `model` : int - 1 = Constant only, 2 = Constant and linear trend (default)
- `pmax` : int - Maximum number of lags (default: 8)
- `fmax` : int - Maximum Fourier frequency, 1-5 (default: 5)
- `ic` : int - Information criterion: 1=AIC, 2=SIC, 3=t-stat (default: 3)
- `verbose` : bool - Print results (default: True)

**Returns:** `FourierGLSResult` object

#### `fourier_gls_f_test(y, model, k, p=0, verbose=True)`

Tests significance of Fourier terms (H0: γ₁ = γ₂ = 0).

#### `gls_detrend(y, z, cbar, return_ssr=False)`

Performs GLS detrending using the Elliott, Rothenberg & Stock (1996) procedure.

### Result Object

The `FourierGLSResult` object contains:

| Attribute | Description |
|-----------|-------------|
| `statistic` | Test statistic (t-ratio) |
| `frequency` | Selected Fourier frequency |
| `lags` | Number of lags selected |
| `critical_values` | Array of [1%, 5%, 10%] critical values |
| `model` | Model specification (1 or 2) |
| `T` | Sample size |
| `conclusion` | Test conclusion at 5% level |

Methods:
- `summary()` : Returns formatted summary string
- `to_dict()` : Converts results to dictionary

### Critical Values

```python
from fourier_gls import get_cbar, get_fourier_gls_critical_values

# Get c-bar parameter (Table 1)
cbar = get_cbar(model=2, k=1)  # Returns -22.00

# Get critical values (Table 2)
cv = get_fourier_gls_critical_values(T=200, model=2)
```

## Model Specifications

### Model 1: Constant Only

$$y_t = \delta_0 + \gamma_1 \sin\left(\frac{2\pi k t}{T}\right) + \gamma_2 \cos\left(\frac{2\pi k t}{T}\right) + x_t$$

### Model 2: Constant and Trend

$$y_t = \delta_0 + \delta_1 t + \gamma_1 \sin\left(\frac{2\pi k t}{T}\right) + \gamma_2 \cos\left(\frac{2\pi k t}{T}\right) + x_t$$

where $x_t = \rho x_{t-1} + u_t$ and $u_t \sim \text{iid}(0, \sigma^2)$.

## Examples

### Basic Usage

```python
import numpy as np
from fourier_gls import fourier_gls

# Load your data
y = np.loadtxt('your_data.csv')

# Test with constant + trend model
result = fourier_gls(y, model=2)
print(f"Test statistic: {result.statistic:.4f}")
print(f"Selected frequency: k = {result.frequency}")
```

### Comparing Different Tests

```python
from fourier_gls import fourier_gls, fourier_df, fourier_lm

y = np.random.randn(200).cumsum()

# GLS de-trended test
gls_result = fourier_gls(y, model=2, verbose=False)

# OLS de-trended test  
df_result = fourier_df(y, model=2, verbose=False)

# LM test
lm_result = fourier_lm(y, verbose=False)

print(f"GLS statistic: {gls_result.statistic:.4f}")
print(f"DF statistic:  {df_result.statistic:.4f}")
print(f"LM statistic:  {lm_result.statistic:.4f}")
```

### Fixed Frequency Test

```python
from fourier_gls import fourier_gls_fixed_k

# Use k=1 (single break-like behavior)
result = fourier_gls_fixed_k(y, model=2, k=1)
```

### Testing for Fourier Term Significance

```python
from fourier_gls import fourier_gls_f_test

# Test if Fourier terms are significant
f_result = fourier_gls_f_test(y, model=2, k=1, p=2)
```

### Simulating Critical Values

```python
from fourier_gls import simulate_critical_values

# Generate custom critical values
cv = simulate_critical_values(T=150, model=2, k=1, n_simulations=10000, seed=42)
print(f"Critical values (1%, 5%, 10%): {cv}")
```

## Critical Values Tables

### Table 1: Local GLS De-trending Parameters (c̄)

| k | Constant (c̄_κ) | Constant + Trend (c̄_τ) |
|---|-----------------|-------------------------|
| 0 | -7.00 | -13.50 |
| 1 | -12.25 | -22.00 |
| 2 | -8.25 | -16.25 |
| 3 | -7.75 | -14.75 |
| 4 | -7.50 | -14.25 |
| 5 | -7.25 | -14.00 |

### Table 2: Critical Values for t^{ERS}_f Tests

Sample critical values for T = 200, Constant + Trend model:

| k | 1% | 5% | 10% |
|---|-----|-----|------|
| 1 | -4.593 | -4.041 | -3.749 |
| 2 | -4.191 | -3.569 | -3.228 |
| 3 | -3.993 | -3.300 | -2.950 |
| 4 | -3.852 | -3.174 | -2.852 |
| 5 | -3.749 | -3.075 | -2.761 |

## Compatibility

This implementation is designed to be fully compatible with the original GAUSS code by Saban Nazlioglu and matches the methodology in Rodrigues & Taylor (2012).

## Requirements

- Python >= 3.8
- NumPy >= 1.20.0
- SciPy >= 1.7.0

## Author

**Dr. Merwan Roudane**  
Email: merwanroudane920@gmail.com  
GitHub: https://github.com/merwanroudane/fouriergls

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use this package in academic work, please cite:

```bibtex
@article{rodrigues2012flexible,
  title={The Flexible Fourier Form and Local Generalised Least Squares De-trended Unit Root Tests},
  author={Rodrigues, Paulo MM and Taylor, A M Robert},
  journal={Oxford Bulletin of Economics and Statistics},
  volume={74},
  number={5},
  pages={736--759},
  year={2012}
}

@software{roudane2024fouriergls,
  author = {Roudane, Merwan},
  title = {fourier\_gls: Python Implementation of Fourier GLS Unit Root Tests},
  year = {2024},
  url = {https://github.com/merwanroudane/fouriergls}
}
```

## Related Papers

1. Elliott, G., Rothenberg, T. J., & Stock, J. H. (1996). Efficient tests for an autoregressive unit root. *Econometrica*, 64, 813-836.

2. Enders, W., & Lee, J. (2012). A Unit Root Test Using a Fourier Series to Approximate Smooth Breaks. *Oxford Bulletin of Economics and Statistics*, 74(4), 574-599.

3. Becker, R., Enders, W., & Lee, J. (2006). A stationarity test in the presence of an unknown number of smooth breaks. *Journal of Time Series Analysis*, 27, 381-409.
