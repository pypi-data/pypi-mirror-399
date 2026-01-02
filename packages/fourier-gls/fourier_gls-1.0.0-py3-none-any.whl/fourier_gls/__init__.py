"""
Fourier GLS Unit Root Test Library
===================================

A Python implementation of the Flexible Fourier Form and Local Generalised
Least Squares De-trended Unit Root Tests.

Reference:
    Rodrigues, P. M. M and Taylor, A. M. R. (2012),
    "The Flexible Fourier Form and Local Generalised Least Squares
     De-trended Unit Root Tests."
    Oxford Bulletin of Economics and Statistics, 74, 5 (2012), 736-759.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/fouriergls

Original GAUSS code by Saban Nazlioglu
"""

from .fourier_gls import (
    fourier_gls,
    fourier_gls_fixed_k,
    fourier_gls_f_test,
    fourier_df,
    fourier_lm,
    gls_detrend,
    FourierGLSResult,
    FourierGLSFTestResult,
)

from .critical_values import (
    get_cbar,
    get_fourier_gls_critical_values,
    get_fourier_gls_critical_values_multiple,
    simulate_critical_values,
)

from .utils import (
    diff,
    lagn,
    trimr,
    get_fourier_terms,
    ols,
    get_lag_by_ic,
)

from .version import __version__

__all__ = [
    # Main functions
    'fourier_gls',
    'fourier_gls_fixed_k',
    'fourier_gls_f_test',
    'fourier_df',
    'fourier_lm',
    'gls_detrend',
    # Result classes
    'FourierGLSResult',
    'FourierGLSFTestResult',
    # Critical value functions
    'get_cbar',
    'get_fourier_gls_critical_values',
    'get_fourier_gls_critical_values_multiple',
    'simulate_critical_values',
    # Utility functions
    'diff',
    'lagn',
    'trimr',
    'get_fourier_terms',
    'ols',
    'get_lag_by_ic',
    # Version
    '__version__',
]
