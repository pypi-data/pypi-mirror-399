"""
Utility functions for Fourier GLS tests.

This module provides helper functions that replicate GAUSS behavior
for array manipulation, OLS estimation, and Fourier term generation.

Reference:
    Rodrigues, P. M. M and Taylor, A. M. R. (2012),
    "The Flexible Fourier Form and Local Generalised Least Squares
     De-trended Unit Root Tests."
    Oxford Bulletin of Economics and Statistics, 74, 5 (2012), 736-759.
"""

import numpy as np
from typing import Tuple, Optional, Union, List


def diff(y: np.ndarray, order: int = 1) -> np.ndarray:
    """
    Compute the difference of a time series.
    
    Replicates GAUSS diff() function behavior.
    The first 'order' observations are set to NaN.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series (T x 1) or (T,)
    order : int, optional
        Order of differencing, by default 1
    
    Returns
    -------
    np.ndarray
        Differenced series with NaN for first 'order' observations
    
    Examples
    --------
    >>> y = np.array([1.0, 3.0, 6.0, 10.0, 15.0])
    >>> diff(y, 1)
    array([nan,  2.,  3.,  4.,  5.])
    """
    y = np.asarray(y).flatten()
    T = len(y)
    result = np.full(T, np.nan)
    
    if order >= T:
        return result
    
    result[order:] = y[order:] - y[:-order]
    return result


def lagn(y: np.ndarray, lags: Union[int, np.ndarray, List[int]]) -> np.ndarray:
    """
    Create lagged values of a time series.
    
    Replicates GAUSS lagn() function behavior.
    Missing values at the beginning are set to NaN.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series (T x 1) or (T,)
    lags : int or array-like
        If int: number of lags (creates single lagged series)
        If array-like: creates multiple lagged series for each lag value
    
    Returns
    -------
    np.ndarray
        Lagged series. If lags is an array, returns (T x len(lags)) matrix
    
    Examples
    --------
    >>> y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> lagn(y, 1)
    array([nan,  1.,  2.,  3.,  4.])
    >>> lagn(y, np.array([1, 2]))
    array([[nan, nan],
           [ 1., nan],
           [ 2.,  1.],
           [ 3.,  2.],
           [ 4.,  3.]])
    """
    y = np.asarray(y).flatten()
    T = len(y)
    
    if isinstance(lags, (int, float)):
        lags = [int(lags)]
    else:
        lags = [int(l) for l in np.asarray(lags).flatten()]
    
    n_lags = len(lags)
    
    if n_lags == 1:
        lag = lags[0]
        result = np.full(T, np.nan)
        if lag < T and lag > 0:
            result[lag:] = y[:-lag]
        elif lag == 0:
            result = y.copy()
        return result
    else:
        result = np.full((T, n_lags), np.nan)
        for i, lag in enumerate(lags):
            if lag < T and lag > 0:
                result[lag:, i] = y[:-lag]
            elif lag == 0:
                result[:, i] = y
        return result


def trimr(x: np.ndarray, top: int, bot: int) -> np.ndarray:
    """
    Trim rows from top and bottom of a matrix.
    
    Replicates GAUSS trimr() function behavior.
    
    Parameters
    ----------
    x : np.ndarray
        Input matrix or vector
    top : int
        Number of rows to remove from the top
    bot : int
        Number of rows to remove from the bottom
    
    Returns
    -------
    np.ndarray
        Trimmed matrix
    
    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> trimr(x, 1, 1)
    array([2, 3, 4])
    """
    x = np.asarray(x)
    
    if x.ndim == 1:
        T = len(x)
        if top + bot >= T:
            return np.array([])
        if bot == 0:
            return x[top:]
        else:
            return x[top:-bot] if bot > 0 else x[top:]
    else:
        T = x.shape[0]
        if top + bot >= T:
            return np.array([]).reshape(0, x.shape[1])
        if bot == 0:
            return x[top:, :]
        else:
            return x[top:-bot, :] if bot > 0 else x[top:, :]


def get_fourier_terms(T: int, k: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate Fourier sine and cosine terms.
    
    Creates sin(2*pi*k*t/T) and cos(2*pi*k*t/T) for t = 1, ..., T.
    
    This follows equation (1) from Rodrigues & Taylor (2012):
    y_t = δ_0 + δ_1*t + γ_1*sin(2πkt/T) + γ_2*cos(2πkt/T) + x_t
    
    Parameters
    ----------
    T : int
        Sample size
    k : int
        Fourier frequency (1 <= k <= 5)
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        sin_term : (T,) array of sine values
        cos_term : (T,) array of cosine values
    
    Examples
    --------
    >>> sink, cosk = get_fourier_terms(100, 1)
    >>> sink.shape
    (100,)
    """
    t = np.arange(1, T + 1)
    sin_term = np.sin(2 * np.pi * k * t / T)
    cos_term = np.cos(2 * np.pi * k * t / T)
    return sin_term, cos_term


def ols(y: np.ndarray, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float, np.ndarray, float]:
    """
    Ordinary Least Squares estimation.
    
    Replicates GAUSS myols() function behavior.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (T x 1) or (T,)
    X : np.ndarray
        Independent variables (T x k)
    
    Returns
    -------
    Tuple containing:
        b : np.ndarray
            Coefficient estimates (k x 1)
        e : np.ndarray
            Residuals (T x 1)
        sig2 : float
            Variance of residuals (SSR / (T - k))
        se : np.ndarray
            Standard errors of coefficients (k x 1)
        ssr : float
            Sum of squared residuals
    
    Examples
    --------
    >>> y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> X = np.column_stack([np.ones(5), np.arange(1, 6)])
    >>> b, e, sig2, se, ssr = ols(y, X)
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T, k = X.shape
    
    # Coefficient estimates: b = (X'X)^(-1) X'y
    XtX = X.T @ X
    Xty = X.T @ y
    
    # Use pseudo-inverse for numerical stability
    try:
        XtX_inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        XtX_inv = np.linalg.pinv(XtX)
    
    b = XtX_inv @ Xty
    
    # Residuals
    e = y - X @ b
    
    # Sum of squared residuals
    ssr = float(e.T @ e)
    
    # Variance estimate
    df = T - k
    sig2 = ssr / df if df > 0 else np.nan
    
    # Standard errors
    var_b = sig2 * XtX_inv
    se = np.sqrt(np.diag(var_b))
    
    return b, e, sig2, se, ssr


def get_lag_by_ic(ic: int, pmax: int, 
                   aic: np.ndarray, 
                   sic: np.ndarray, 
                   tstat: np.ndarray,
                   significance_level: float = 1.645) -> int:
    """
    Select optimal lag length by information criterion.
    
    Replicates GAUSS _get_lag() function behavior.
    
    Parameters
    ----------
    ic : int
        Information criterion:
        1 = Akaike Information Criterion (AIC)
        2 = Schwarz Information Criterion (SIC/BIC)
        3 = t-statistic significance (sequential testing)
    pmax : int
        Maximum number of lags
    aic : np.ndarray
        AIC values for each lag (pmax+1 x 1)
    sic : np.ndarray
        SIC values for each lag (pmax+1 x 1)
    tstat : np.ndarray
        t-statistics for last lag coefficient (pmax+1 x 1)
    significance_level : float, optional
        Critical value for t-stat method, by default 1.645 (10% two-sided)
    
    Returns
    -------
    int
        Optimal lag (1-indexed for compatibility with GAUSS)
    
    Notes
    -----
    For ic=3 (t-stat), starts from pmax and works down until finding
    a significant last lag coefficient, or returns 1 if none significant.
    """
    if ic == 1:  # AIC
        return int(np.argmin(aic) + 1)
    elif ic == 2:  # SIC
        return int(np.argmin(sic) + 1)
    elif ic == 3:  # t-stat significance
        # Start from pmax and go down
        for p in range(pmax, 0, -1):
            if np.abs(tstat[p]) > significance_level:
                return p + 1
        return 1
    else:
        raise ValueError(f"Invalid information criterion: {ic}. Use 1 (AIC), 2 (SIC), or 3 (t-stat).")


def seqa(start: float, increment: float, n: int) -> np.ndarray:
    """
    Create an arithmetic sequence.
    
    Replicates GAUSS seqa() function.
    
    Parameters
    ----------
    start : float
        Starting value
    increment : float
        Increment between values
    n : int
        Number of elements
    
    Returns
    -------
    np.ndarray
        Arithmetic sequence of length n
    
    Examples
    --------
    >>> seqa(1, 1, 5)
    array([1., 2., 3., 4., 5.])
    """
    return np.arange(start, start + n * increment, increment)[:n].astype(float)


def check_for_missing(y: np.ndarray, func_name: str = "function") -> None:
    """
    Check for missing values in input data.
    
    Replicates GAUSS _checkForMissings() function.
    
    Parameters
    ----------
    y : np.ndarray
        Input data to check
    func_name : str, optional
        Function name for error message
    
    Raises
    ------
    ValueError
        If missing values are found in the data
    """
    y = np.asarray(y)
    if np.any(np.isnan(y)):
        raise ValueError(f"{func_name}: Input data contains missing values (NaN).")
    if np.any(np.isinf(y)):
        raise ValueError(f"{func_name}: Input data contains infinite values.")


def estimate_frequency(y: np.ndarray, model: int, fmax: int = 5) -> int:
    """
    Estimate optimal Fourier frequency using the Davies (1987) approach.
    
    Minimizes the residual sum of squares from regression of y on
    deterministic components including Fourier terms.
    
    This implements the data-driven frequency selection discussed in
    Rodrigues & Taylor (2012, Section III) and Becker et al. (2006).
    
    Parameters
    ----------
    y : np.ndarray
        Time series data (T x 1) or (T,)
    model : int
        1 = Constant only
        2 = Constant and linear trend
    fmax : int, optional
        Maximum frequency to consider, by default 5
    
    Returns
    -------
    int
        Optimal frequency (1 <= k <= fmax)
    
    References
    ----------
    Davies, R. B. (1987). "Hypothesis testing when a nuisance parameter 
    is present only under the alternative." Biometrika, 74, 33-43.
    """
    y = np.asarray(y).flatten()
    T = len(y)
    
    ssr_k = np.zeros(fmax)
    
    for k in range(1, fmax + 1):
        # Get Fourier terms
        sink, cosk = get_fourier_terms(T, k)
        
        # Build regressor matrix
        if model == 1:
            # Constant + Fourier terms (equation 11 in paper)
            X = np.column_stack([np.ones(T), sink, cosk])
        else:
            # Constant + trend + Fourier terms
            X = np.column_stack([np.ones(T), np.arange(1, T + 1), sink, cosk])
        
        # OLS estimation
        _, _, _, _, ssr = ols(y, X)
        ssr_k[k - 1] = ssr
    
    # Return frequency that minimizes SSR (1-indexed)
    return int(np.argmin(ssr_k) + 1)
