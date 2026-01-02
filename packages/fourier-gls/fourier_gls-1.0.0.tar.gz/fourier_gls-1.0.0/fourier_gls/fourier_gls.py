"""
Fourier GLS Unit Root Tests.

This module implements the Flexible Fourier Form and Local Generalised
Least Squares De-trended Unit Root Tests from Rodrigues & Taylor (2012).

Main functions:
    - fourier_gls: Main unit root test with automatic frequency selection
    - fourier_gls_f_test: F-test for linearity (testing significance of Fourier terms)
    - gls_detrend: GLS detrending procedure

Reference:
    Rodrigues, P. M. M and Taylor, A. M. R. (2012),
    "The Flexible Fourier Form and Local Generalised Least Squares
     De-trended Unit Root Tests."
    Oxford Bulletin of Economics and Statistics, 74, 5 (2012), 736-759.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/fouriergls
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional, Union, List

from .utils import (
    diff, lagn, trimr, get_fourier_terms, ols, 
    get_lag_by_ic, check_for_missing
)
from .critical_values import (
    get_cbar, get_fourier_gls_critical_values,
    get_df_critical_values, get_lm_critical_values
)


@dataclass
class FourierGLSResult:
    """
    Results from the Fourier GLS unit root test.
    
    Attributes
    ----------
    statistic : float
        The GLS test statistic (t-ratio for ρ = 0)
    frequency : int
        Selected Fourier frequency (k = 1, ..., fmax)
    lags : int
        Number of lags selected by information criterion
    critical_values : np.ndarray
        Critical values at 1%, 5%, 10% significance levels
    model : int
        Model specification (1 = constant, 2 = constant + trend)
    T : int
        Sample size
    conclusion : str
        Test conclusion at 5% level
    pvalue_approx : float
        Approximate p-value (based on linear interpolation)
    
    Notes
    -----
    The test rejects the null hypothesis of a unit root when the 
    test statistic is less than (more negative than) the critical value.
    """
    statistic: float
    frequency: int
    lags: int
    critical_values: np.ndarray
    model: int
    T: int
    conclusion: str
    pvalue_approx: Optional[float] = None
    
    def __repr__(self) -> str:
        model_str = "Constant" if self.model == 1 else "Constant + Trend"
        
        result = f"""
================================================================================
                    Fourier GLS Unit Root Test Results
================================================================================
Reference: Rodrigues & Taylor (2012), Oxford Bulletin of Economics and Statistics

Model:               {model_str}
Sample Size:         {self.T}
Selected Frequency:  k = {self.frequency}
Selected Lags:       {self.lags}

--------------------------------------------------------------------------------
Test Statistic:      {self.statistic:.4f}
--------------------------------------------------------------------------------

Critical Values:
    1%:   {self.critical_values[0]:.4f}
    5%:   {self.critical_values[1]:.4f}
    10%:  {self.critical_values[2]:.4f}

--------------------------------------------------------------------------------
Conclusion (5% level): {self.conclusion}
================================================================================
"""
        return result
    
    def summary(self) -> str:
        """Return a formatted summary string for publication."""
        return self.__repr__()
    
    def to_dict(self) -> dict:
        """Convert results to dictionary format."""
        return {
            'statistic': self.statistic,
            'frequency': self.frequency,
            'lags': self.lags,
            'critical_values': {
                '1%': self.critical_values[0],
                '5%': self.critical_values[1],
                '10%': self.critical_values[2]
            },
            'model': self.model,
            'T': self.T,
            'conclusion': self.conclusion,
            'pvalue_approx': self.pvalue_approx
        }


@dataclass
class FourierGLSFTestResult:
    """
    Results from the Fourier GLS F-test for linearity.
    
    This tests the null hypothesis that Fourier terms are not needed
    (i.e., H0: γ_1 = γ_2 = 0 in the deterministic component).
    
    Attributes
    ----------
    f_statistic : float
        The F-statistic
    critical_values : np.ndarray
        F critical values at 1%, 5%, 10% levels
    frequency : int
        Fourier frequency tested
    lags : int
        Number of lags used
    model : int
        Model specification
    conclusion : str
        Test conclusion at 5% level
    """
    f_statistic: float
    critical_values: np.ndarray
    frequency: int
    lags: int
    model: int
    conclusion: str
    
    def __repr__(self) -> str:
        model_str = "Constant" if self.model == 1 else "Constant + Trend"
        
        return f"""
================================================================================
              Fourier GLS F-Test for Linearity
================================================================================
Model:          {model_str}
Frequency:      k = {self.frequency}
Lags:           {self.lags}

F-Statistic:    {self.f_statistic:.4f}

Critical Values (standard F-distribution):
    1%:   {self.critical_values[0]:.4f}
    5%:   {self.critical_values[1]:.4f}
    10%:  {self.critical_values[2]:.4f}

Conclusion (5% level): {self.conclusion}
================================================================================
"""


def gls_detrend(y: np.ndarray, z: np.ndarray, cbar: float,
                 return_ssr: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, float]]:
    """
    Perform GLS detrending as in Elliott, Rothenberg & Stock (1996).
    
    This implements the local GLS de-trending procedure from equations (3)-(4)
    in Rodrigues & Taylor (2012).
    
    Parameters
    ----------
    y : np.ndarray
        Original time series (T x 1) or (T,)
    z : np.ndarray
        Deterministic regressors matrix (T x k)
        For model 1: [ones, sin, cos]
        For model 2: [ones, trend, sin, cos]
    cbar : float
        Local GLS de-trending parameter (c-bar)
    return_ssr : bool, optional
        If True, also return sum of squared residuals from the
        quasi-differenced regression
    
    Returns
    -------
    ygls : np.ndarray
        GLS de-trended series (T,)
    ssr : float (optional)
        Sum of squared residuals (if return_ssr=True)
    
    Notes
    -----
    The procedure follows ERS (1996):
    
    1. Quasi-difference y and z using parameter α = 1 + c̄/T:
       - y_α = (y_1, y_2 - α*y_1, ..., y_T - α*y_{T-1})
       - z_α = (z_1, z_2 - α*z_1, ..., z_T - α*z_{T-1})
    
    2. Estimate β̂ from regressing y_α on z_α:
       β̂ = (z_α' z_α)^{-1} z_α' y_α
    
    3. Return detrended series: y - z * β̂
    
    Examples
    --------
    >>> y = np.random.randn(100)
    >>> z = np.column_stack([np.ones(100), np.sin(2*np.pi*np.arange(1,101)/100)])
    >>> ygls = gls_detrend(y, z, -7.0)
    """
    y = np.asarray(y).flatten()
    z = np.asarray(z)
    
    if z.ndim == 1:
        z = z.reshape(-1, 1)
    
    T = len(y)
    
    # Local-to-unity parameter
    a = 1 + cbar / T
    
    # Quasi-difference transformation (equations 3-4 in the paper)
    ya = np.zeros(T)
    za = np.zeros((T, z.shape[1]))
    
    # First observation unchanged
    ya[0] = y[0]
    za[0, :] = z[0, :]
    
    # Quasi-differenced observations
    ya[1:] = y[1:] - a * y[:-1]
    za[1:, :] = z[1:, :] - a * z[:-1, :]
    
    # Detrending regression: β̂ = (z_α' z_α)^{-1} z_α' y_α
    try:
        ZtZ_inv = np.linalg.inv(za.T @ za)
    except np.linalg.LinAlgError:
        ZtZ_inv = np.linalg.pinv(za.T @ za)
    
    bhat = ZtZ_inv @ (za.T @ ya)
    
    # GLS de-trended series
    ygls = y - z @ bhat
    
    if return_ssr:
        ua = ya - za @ bhat
        ssr = float(ua.T @ ua)
        return ygls, ssr
    
    return ygls


def fourier_gls(y: np.ndarray, 
                 model: int = 2,
                 pmax: int = 8,
                 fmax: int = 5,
                 ic: int = 3,
                 verbose: bool = True) -> FourierGLSResult:
    """
    Fourier GLS unit root test with data-driven frequency selection.
    
    This is the main test function implementing the procedure from
    Rodrigues & Taylor (2012). The test uses local GLS de-trending
    with Fourier terms to capture unknown structural breaks.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data (T x 1) or (T,)
    model : int, optional
        Deterministic specification:
        1 = Constant only
        2 = Constant and linear trend (default)
    pmax : int, optional
        Maximum number of lags for augmented regression (default: 8)
    fmax : int, optional
        Maximum Fourier frequency to consider (default: 5, upper bound: 5)
    ic : int, optional
        Information criterion for lag selection:
        1 = Akaike (AIC)
        2 = Schwarz (BIC/SIC)
        3 = t-statistic significance (default)
    verbose : bool, optional
        If True, print results summary (default: True)
    
    Returns
    -------
    FourierGLSResult
        Object containing test results, critical values, and conclusion
    
    Notes
    -----
    The test procedure follows these steps:
    
    1. For each frequency k = 1, ..., fmax:
       a. Construct Fourier terms: sin(2πkt/T) and cos(2πkt/T)
       b. Build deterministic regressors z_t
       c. GLS de-trend y using c̄_k from Table 1
       d. Run ADF regression on de-trended series
       e. Select optimal lag by information criterion
       f. Store SSR and t-statistic
    
    2. Select optimal frequency k* that minimizes SSR (Davies, 1987)
    
    3. Return t-statistic for k* and corresponding critical values
    
    The null hypothesis is H0: ρ = 1 (unit root).
    Reject H0 if test statistic < critical value.
    
    References
    ----------
    Rodrigues, P. M. M and Taylor, A. M. R. (2012),
    "The Flexible Fourier Form and Local Generalised Least Squares
     De-trended Unit Root Tests."
    Oxford Bulletin of Economics and Statistics, 74, 5 (2012), 736-759.
    
    Examples
    --------
    >>> import numpy as np
    >>> from fourier_gls import fourier_gls
    >>> 
    >>> # Generate unit root process with structural break
    >>> np.random.seed(42)
    >>> T = 200
    >>> y = np.cumsum(np.random.randn(T)) + 5 * np.sin(2 * np.pi * np.arange(T) / T)
    >>> 
    >>> # Run test
    >>> result = fourier_gls(y, model=2)
    >>> print(result)
    """
    # Input validation
    y = np.asarray(y).flatten()
    check_for_missing(y, "fourier_gls")
    
    if model not in [1, 2]:
        raise ValueError("model must be 1 (constant) or 2 (constant + trend)")
    
    if pmax < 0:
        raise ValueError("pmax must be non-negative")
    
    if fmax < 1 or fmax > 5:
        raise ValueError("fmax must be between 1 and 5")
    
    if ic not in [1, 2, 3]:
        raise ValueError("ic must be 1 (AIC), 2 (SIC), or 3 (t-stat)")
    
    T = len(y)
    
    # Storage arrays
    taup = np.zeros(pmax + 1)
    aicp = np.zeros(pmax + 1)
    sicp = np.zeros(pmax + 1)
    tstatp = np.zeros(pmax + 1)
    ssrp = np.zeros(pmax + 1)
    
    ssrk = np.zeros(fmax)
    tauk = np.zeros(fmax)
    keep_p = np.zeros(fmax, dtype=int)
    
    # Loop over frequencies k = 1, ..., fmax
    for k in range(1, fmax + 1):
        # Get c-bar for this model and frequency
        cbar = get_cbar(model, k)
        
        # Generate Fourier terms (equation 1 in paper)
        sink, cosk = get_fourier_terms(T, k)
        
        # Build deterministic regressors z
        if model == 1:
            # Constant + Fourier
            z = np.column_stack([np.ones(T), sink, cosk])
        else:
            # Constant + trend + Fourier
            z = np.column_stack([np.ones(T), np.arange(1, T + 1), sink, cosk])
        
        # GLS detrending (equations 3-5 in paper)
        ygls = gls_detrend(y, z, cbar)
        
        # Compute first difference and lag
        dy = diff(ygls, 1)
        ly = lagn(ygls, 1)
        
        # Create lag matrix for ADF augmentation
        if pmax > 0:
            lmat = lagn(dy, np.arange(1, pmax + 1))
        else:
            lmat = None
        
        # Loop over lag lengths p = 0, ..., pmax
        for p in range(pmax + 1):
            # Trim data to remove NaN from differencing/lagging
            dep = trimr(dy, p + 1, 0)
            y1 = trimr(ly, p + 1, 0)
            
            # Build regressor matrix for ADF regression
            if p == 0:
                X = y1.reshape(-1, 1)
            else:
                ldy = trimr(lmat[:, :p], p + 1, 0)
                X = np.column_stack([y1, ldy])
            
            # OLS estimation (equation 5 in paper)
            b, e, sig2, se, ssr = ols(dep, X)
            
            # Store results
            n_obs = len(dep)
            taup[p] = b[0] / se[0]  # t-statistic for rho
            
            # Information criteria
            # AIC = ln(SSR/n) + 2*(k+2)/n  (matching GAUSS code)
            aicp[p] = np.log(e.T @ e / n_obs) + 2 * (k + 2) / n_obs
            
            # SIC = ln(SSR/n) + (cols(z)+2)*ln(n)/n
            sicp[p] = np.log(e.T @ e / n_obs) + (X.shape[1] + 2) * np.log(n_obs) / n_obs
            
            # t-stat for last lag (for sequential testing)
            tstatp[p] = b[-1] / se[-1]
            ssrp[p] = ssr
        
        # Select optimal lag by information criterion
        p_opt = get_lag_by_ic(ic, pmax, aicp, sicp, tstatp)
        
        # Store results for this frequency
        keep_p[k - 1] = p_opt
        ssrk[k - 1] = ssrp[p_opt - 1]  # p_opt is 1-indexed
        tauk[k - 1] = taup[p_opt - 1]
    
    # Select optimal frequency (minimizes SSR - Davies, 1987)
    f_opt = int(np.argmin(ssrk) + 1)  # 1-indexed frequency
    
    # Get test statistic and lag for optimal frequency
    gls_stat = tauk[f_opt - 1]
    opt_lag = keep_p[f_opt - 1] - 1  # Convert to 0-indexed lag count
    
    # Get critical values from Table 2
    crit = get_fourier_gls_critical_values(T, model)
    cv = crit[f_opt - 1, :]  # Row for selected frequency
    
    # Determine conclusion
    if gls_stat < cv[1]:  # Compare with 5% CV
        conclusion = "Reject H0: Evidence against unit root at 5% level"
    else:
        conclusion = "Fail to reject H0: No evidence against unit root at 5% level"
    
    # Create result object
    result = FourierGLSResult(
        statistic=gls_stat,
        frequency=f_opt,
        lags=opt_lag,
        critical_values=cv,
        model=model,
        T=T,
        conclusion=conclusion
    )
    
    if verbose:
        print(result)
    
    return result


def fourier_gls_fixed_k(y: np.ndarray,
                        model: int,
                        k: int,
                        pmax: int = 8,
                        ic: int = 3,
                        verbose: bool = False) -> FourierGLSResult:
    """
    Fourier GLS unit root test with fixed (known) frequency.
    
    Use this when the Fourier frequency is known or pre-specified,
    rather than data-driven selection.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data
    model : int
        1 = Constant, 2 = Constant + trend
    k : int
        Fixed Fourier frequency (1-5)
    pmax : int, optional
        Maximum lags (default: 8)
    ic : int, optional
        Information criterion (default: 3)
    verbose : bool, optional
        Print results (default: False)
    
    Returns
    -------
    FourierGLSResult
        Test results
    """
    y = np.asarray(y).flatten()
    check_for_missing(y, "fourier_gls_fixed_k")
    
    if k < 1 or k > 5:
        raise ValueError("k must be between 1 and 5")
    
    T = len(y)
    
    # Get c-bar for this frequency
    cbar = get_cbar(model, k)
    
    # Generate Fourier terms
    sink, cosk = get_fourier_terms(T, k)
    
    # Build deterministic regressors
    if model == 1:
        z = np.column_stack([np.ones(T), sink, cosk])
    else:
        z = np.column_stack([np.ones(T), np.arange(1, T + 1), sink, cosk])
    
    # GLS detrending
    ygls = gls_detrend(y, z, cbar)
    
    # Storage
    taup = np.zeros(pmax + 1)
    aicp = np.zeros(pmax + 1)
    sicp = np.zeros(pmax + 1)
    tstatp = np.zeros(pmax + 1)
    
    # Compute differences and lags
    dy = diff(ygls, 1)
    ly = lagn(ygls, 1)
    
    if pmax > 0:
        lmat = lagn(dy, np.arange(1, pmax + 1))
    
    # Loop over lags
    for p in range(pmax + 1):
        dep = trimr(dy, p + 1, 0)
        y1 = trimr(ly, p + 1, 0)
        
        if p == 0:
            X = y1.reshape(-1, 1)
        else:
            ldy = trimr(lmat[:, :p], p + 1, 0)
            X = np.column_stack([y1, ldy])
        
        b, e, sig2, se, ssr = ols(dep, X)
        
        n_obs = len(dep)
        taup[p] = b[0] / se[0]
        aicp[p] = np.log(e.T @ e / n_obs) + 2 * (k + 2) / n_obs
        sicp[p] = np.log(e.T @ e / n_obs) + (X.shape[1] + 2) * np.log(n_obs) / n_obs
        tstatp[p] = b[-1] / se[-1]
    
    # Select optimal lag
    p_opt = get_lag_by_ic(ic, pmax, aicp, sicp, tstatp)
    opt_lag = p_opt - 1
    gls_stat = taup[p_opt - 1]
    
    # Get critical values
    crit = get_fourier_gls_critical_values(T, model)
    cv = crit[k - 1, :]
    
    # Conclusion
    if gls_stat < cv[1]:
        conclusion = "Reject H0: Evidence against unit root at 5% level"
    else:
        conclusion = "Fail to reject H0: No evidence against unit root at 5% level"
    
    result = FourierGLSResult(
        statistic=gls_stat,
        frequency=k,
        lags=opt_lag,
        critical_values=cv,
        model=model,
        T=T,
        conclusion=conclusion
    )
    
    if verbose:
        print(result)
    
    return result


def fourier_gls_f_test(y: np.ndarray,
                        model: int,
                        k: int,
                        p: int = 0,
                        verbose: bool = True) -> FourierGLSFTestResult:
    """
    F-test for significance of Fourier terms.
    
    Tests the null hypothesis H0: γ_1 = γ_2 = 0, i.e., that the
    Fourier terms are not needed in the deterministic component.
    
    This implements the test discussed in Rodrigues & Taylor (2012)
    and corresponds to fourierGLSFTest in the GAUSS code.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data
    model : int
        1 = Constant only
        2 = Constant and trend
    k : int
        Fourier frequency to test
    p : int, optional
        Number of lags in ADF regression (default: 0)
    verbose : bool, optional
        Print results (default: True)
    
    Returns
    -------
    FourierGLSFTestResult
        F-test results
    
    Notes
    -----
    The test compares:
    - Restricted model: without Fourier terms
    - Unrestricted model: with Fourier terms
    
    The F-statistic follows standard F-distribution under the null.
    """
    y = np.asarray(y).flatten()
    check_for_missing(y, "fourier_gls_f_test")
    
    T = len(y)
    cbar = get_cbar(model, k)
    
    # Generate Fourier terms
    sink, cosk = get_fourier_terms(T, k)
    
    # Restricted model (without Fourier terms)
    if model == 1:
        z1 = np.ones((T, 1))
    else:
        z1 = np.column_stack([np.ones(T), np.arange(1, T + 1)])
    
    # Unrestricted model (with Fourier terms)
    z2 = np.column_stack([z1, sink, cosk])
    
    # GLS detrending for both models
    ygls1 = gls_detrend(y, z1, cbar)
    ygls2 = gls_detrend(y, z2, cbar)
    
    # Prepare data for ADF regressions
    dy1 = diff(ygls1, 1)
    ly1 = lagn(ygls1, 1)
    
    dy2 = diff(ygls2, 1)
    ly2 = lagn(ygls2, 1)
    
    # Build regressor matrices
    if p == 0:
        # Restricted
        dep1 = trimr(dy1, 1, 0)
        X1 = trimr(ly1, 1, 0).reshape(-1, 1)
        
        # Unrestricted
        dep2 = trimr(dy2, 1, 0)
        X2 = trimr(ly2, 1, 0).reshape(-1, 1)
    else:
        lmat1 = lagn(dy1, np.arange(1, p + 1))
        lmat2 = lagn(dy2, np.arange(1, p + 1))
        
        dep1 = trimr(dy1, p + 1, 0)
        y1_r = trimr(ly1, p + 1, 0)
        ldy1 = trimr(lmat1, p + 1, 0)
        X1 = np.column_stack([y1_r, ldy1])
        
        dep2 = trimr(dy2, p + 1, 0)
        y2_r = trimr(ly2, p + 1, 0)
        ldy2 = trimr(lmat2, p + 1, 0)
        X2 = np.column_stack([y2_r, ldy2])
    
    # OLS for restricted model
    _, e1, _, _, ssr1 = ols(dep1, X1)
    
    # OLS for unrestricted model
    _, e2, _, _, ssr2 = ols(dep2, X2)
    
    # F-statistic
    q = 2  # Number of restrictions (two Fourier coefficients)
    n = len(dep1)
    k1 = X1.shape[1]
    k2 = X2.shape[1]
    
    # F = ((SSR_r - SSR_u) / q) / (SSR_u / (n - k_u))
    f_stat = ((ssr1 - ssr2) / q) / (ssr2 / (n - k2))
    
    # Critical values from F-distribution
    from scipy import stats
    cv_fstat = np.array([
        stats.f.ppf(0.99, q, n - k2),
        stats.f.ppf(0.95, q, n - k2),
        stats.f.ppf(0.90, q, n - k2)
    ])
    
    # Conclusion
    if f_stat > cv_fstat[1]:  # Compare with 5% CV
        conclusion = "Reject H0: Fourier terms are significant at 5% level"
    else:
        conclusion = "Fail to reject H0: Fourier terms not significant at 5% level"
    
    result = FourierGLSFTestResult(
        f_statistic=f_stat,
        critical_values=cv_fstat,
        frequency=k,
        lags=p,
        model=model,
        conclusion=conclusion
    )
    
    if verbose:
        print(result)
    
    return result


def fourier_df(y: np.ndarray,
               model: int = 2,
               pmax: int = 8,
               fmax: int = 5,
               ic: int = 3,
               verbose: bool = True) -> FourierGLSResult:
    """
    Fourier DF (OLS de-trended) unit root test.
    
    This implements the OLS de-trended Dickey-Fuller test with
    Fourier terms from Enders & Lee (2009), as discussed in
    Rodrigues & Taylor (2012).
    
    Parameters
    ----------
    y : np.ndarray
        Time series data
    model : int
        1 = Constant, 2 = Constant + trend
    pmax : int
        Maximum lags
    fmax : int
        Maximum frequency
    ic : int
        Information criterion
    verbose : bool
        Print results
    
    Returns
    -------
    FourierGLSResult
        Test results (using DF critical values)
    
    Notes
    -----
    The DF test differs from GLS test in using OLS de-trending
    instead of local GLS de-trending. This corresponds to
    equations (7)-(8) in Rodrigues & Taylor (2012).
    """
    y = np.asarray(y).flatten()
    check_for_missing(y, "fourier_df")
    
    T = len(y)
    
    ssrk = np.zeros(fmax)
    tauk = np.zeros(fmax)
    keep_p = np.zeros(fmax, dtype=int)
    
    for k in range(1, fmax + 1):
        # Generate Fourier terms
        sink, cosk = get_fourier_terms(T, k)
        
        # Build full regressor matrix (including y_{t-1})
        if model == 1:
            z = np.column_stack([np.ones(T), sink, cosk])
        else:
            z = np.column_stack([np.ones(T), np.arange(1, T + 1), sink, cosk])
        
        # First difference
        dy = diff(y, 1)
        ly = lagn(y, 1)
        
        if pmax > 0:
            lmat = lagn(dy, np.arange(1, pmax + 1))
        
        taup = np.zeros(pmax + 1)
        aicp = np.zeros(pmax + 1)
        sicp = np.zeros(pmax + 1)
        tstatp = np.zeros(pmax + 1)
        ssrp = np.zeros(pmax + 1)
        
        for p in range(pmax + 1):
            dep = trimr(dy, p + 1, 0)
            y1 = trimr(ly, p + 1, 0)
            z_trim = trimr(z, p + 1, 0)
            
            # Build regressor matrix: [z, y_{t-1}, lags]
            if p == 0:
                X = np.column_stack([z_trim, y1])
            else:
                ldy = trimr(lmat[:, :p], p + 1, 0)
                X = np.column_stack([z_trim, y1, ldy])
            
            b, e, sig2, se, ssr = ols(dep, X)
            
            n_obs = len(dep)
            # y_{t-1} coefficient is at position after z columns
            y1_pos = z_trim.shape[1]
            
            taup[p] = b[y1_pos] / se[y1_pos]
            aicp[p] = np.log(e.T @ e / n_obs) + 2 * (k + 2) / n_obs
            sicp[p] = np.log(e.T @ e / n_obs) + (X.shape[1] + 2) * np.log(n_obs) / n_obs
            tstatp[p] = b[-1] / se[-1]
            ssrp[p] = ssr
        
        p_opt = get_lag_by_ic(ic, pmax, aicp, sicp, tstatp)
        keep_p[k - 1] = p_opt
        ssrk[k - 1] = ssrp[p_opt - 1]
        tauk[k - 1] = taup[p_opt - 1]
    
    # Select optimal frequency
    f_opt = int(np.argmin(ssrk) + 1)
    df_stat = tauk[f_opt - 1]
    opt_lag = keep_p[f_opt - 1] - 1
    
    # Get DF critical values
    crit = get_df_critical_values(T, model)
    cv = crit[f_opt - 1, :]
    
    if df_stat < cv[1]:
        conclusion = "Reject H0: Evidence against unit root at 5% level"
    else:
        conclusion = "Fail to reject H0: No evidence against unit root at 5% level"
    
    result = FourierGLSResult(
        statistic=df_stat,
        frequency=f_opt,
        lags=opt_lag,
        critical_values=cv,
        model=model,
        T=T,
        conclusion=conclusion
    )
    
    if verbose:
        print("\n" + "=" * 80)
        print("                    Fourier DF (OLS De-trended) Unit Root Test")
        print("=" * 80)
        print(f"Reference: Enders & Lee (2009), Rodrigues & Taylor (2012)")
        print(result.summary().split("Fourier GLS Unit Root Test Results")[1])
    
    return result


def fourier_lm(y: np.ndarray,
               pmax: int = 8,
               fmax: int = 5,
               ic: int = 3,
               verbose: bool = True) -> FourierGLSResult:
    """
    Fourier LM unit root test (FD de-trended).
    
    This implements the LM-type unit root test of Schmidt & Phillips (1992)
    extended with Fourier terms, as in Enders & Lee (2009).
    
    Parameters
    ----------
    y : np.ndarray
        Time series data
    pmax : int
        Maximum lags
    fmax : int
        Maximum frequency
    ic : int
        Information criterion
    verbose : bool
        Print results
    
    Returns
    -------
    FourierGLSResult
        Test results
    
    Notes
    -----
    The LM test uses first-difference (FD) de-trending and is only
    available for model=2 (constant + trend). This corresponds to
    equation (6) in Rodrigues & Taylor (2012).
    """
    y = np.asarray(y).flatten()
    check_for_missing(y, "fourier_lm")
    
    T = len(y)
    model = 2  # LM test is only for constant + trend
    
    ssrk = np.zeros(fmax)
    tauk = np.zeros(fmax)
    keep_p = np.zeros(fmax, dtype=int)
    
    for k in range(1, fmax + 1):
        # Generate Fourier terms
        sink, cosk = get_fourier_terms(T, k)
        
        # First-difference de-trending (under null hypothesis)
        # Estimate: Δy_t = z_t'θ_1 + f_t(k)'θ + error
        dy = y[1:] - y[:-1]
        z_fd = np.column_stack([np.ones(T - 1), sink[1:], cosk[1:]])
        
        # OLS for FD de-trending
        b_fd, _, _, _, _ = ols(dy, z_fd)
        
        # Construct de-trended series
        # y^{LM}_t = y_t - z_t'θ̃ - f_t'θ̃
        # where θ̃ is estimated under H0
        delta_hat = y[0] - b_fd[0] - b_fd[1] * sink[0] - b_fd[2] * cosk[0]
        
        # Build y^{LM}
        yt_detrended = y.copy()
        for t in range(T):
            det_component = delta_hat + b_fd[1] * sink[t] + b_fd[2] * cosk[t]
            yt_detrended[t] = y[t] - det_component
        
        # LM test regression (equation 6)
        dy_lm = diff(yt_detrended, 1)
        ly_lm = lagn(yt_detrended, 1)
        
        if pmax > 0:
            lmat = lagn(dy_lm, np.arange(1, pmax + 1))
        
        taup = np.zeros(pmax + 1)
        aicp = np.zeros(pmax + 1)
        sicp = np.zeros(pmax + 1)
        tstatp = np.zeros(pmax + 1)
        ssrp = np.zeros(pmax + 1)
        
        for p in range(pmax + 1):
            dep = trimr(dy_lm, p + 1, 0)
            y1 = trimr(ly_lm, p + 1, 0)
            
            # LM regression includes deterministics
            z_t = np.column_stack([
                np.ones(len(dep)),
                sink[p + 2:T + 1] if p + 2 <= T else sink[-len(dep):],
                cosk[p + 2:T + 1] if p + 2 <= T else cosk[-len(dep):]
            ])
            z_t = z_t[:len(dep), :]
            
            if p == 0:
                X = np.column_stack([z_t, y1])
            else:
                ldy = trimr(lmat[:, :p], p + 1, 0)
                X = np.column_stack([z_t, y1, ldy])
            
            b, e, sig2, se, ssr = ols(dep, X)
            
            n_obs = len(dep)
            y1_pos = z_t.shape[1]
            
            taup[p] = b[y1_pos] / se[y1_pos]
            aicp[p] = np.log(e.T @ e / n_obs) + 2 * (k + 2) / n_obs
            sicp[p] = np.log(e.T @ e / n_obs) + (X.shape[1] + 2) * np.log(n_obs) / n_obs
            tstatp[p] = b[-1] / se[-1]
            ssrp[p] = ssr
        
        p_opt = get_lag_by_ic(ic, pmax, aicp, sicp, tstatp)
        keep_p[k - 1] = p_opt
        ssrk[k - 1] = ssrp[p_opt - 1]
        tauk[k - 1] = taup[p_opt - 1]
    
    # Select optimal frequency
    f_opt = int(np.argmin(ssrk) + 1)
    lm_stat = tauk[f_opt - 1]
    opt_lag = keep_p[f_opt - 1] - 1
    
    # Get LM critical values
    crit = get_lm_critical_values(T, model)
    cv = crit[f_opt - 1, :]
    
    if lm_stat < cv[1]:
        conclusion = "Reject H0: Evidence against unit root at 5% level"
    else:
        conclusion = "Fail to reject H0: No evidence against unit root at 5% level"
    
    result = FourierGLSResult(
        statistic=lm_stat,
        frequency=f_opt,
        lags=opt_lag,
        critical_values=cv,
        model=model,
        T=T,
        conclusion=conclusion
    )
    
    if verbose:
        print("\n" + "=" * 80)
        print("                    Fourier LM (FD De-trended) Unit Root Test")
        print("=" * 80)
        print(f"Reference: Schmidt & Phillips (1992), Enders & Lee (2009)")
        print(result.summary().split("Fourier GLS Unit Root Test Results")[1])
    
    return result
