"""
Critical values for Fourier GLS unit root tests.

This module provides:
1. Local GLS de-trending parameters (c-bar) from Table 1
2. Critical values for single and multiple frequencies from Tables 2-3
3. Simulation routines for generating custom critical values

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
from typing import Tuple, Optional, Dict, List, Union
from .utils import get_fourier_terms, ols, diff, lagn, trimr


def get_cbar(model: int, k: int) -> float:
    """
    Get the local GLS de-trending parameter c-bar.
    
    Returns the values from Table 1 of Rodrigues & Taylor (2012).
    These parameters were computed as the 50% point on the power contours
    for T = 1000.
    
    Parameters
    ----------
    model : int
        1 = Constant only (c-bar_kappa)
        2 = Constant and trend (c-bar_tau)
    k : int
        Fourier frequency (0 = no Fourier terms, 1-5 = single frequency)
    
    Returns
    -------
    float
        c-bar parameter value
    
    Raises
    ------
    ValueError
        If model or k is out of valid range
    
    Notes
    -----
    From Table 1 (Rodrigues & Taylor, 2012, p. 4):
    
    k     c-bar_kappa   c-bar_tau
    ----------------------------------
    0     -7.00         -13.50
    1     -12.25        -22.00
    2     -8.25         -16.25
    3     -7.75         -14.75
    4     -7.50         -14.25
    5     -7.25         -14.00
    
    Examples
    --------
    >>> get_cbar(1, 1)  # Constant model, frequency 1
    -12.25
    >>> get_cbar(2, 1)  # Trend model, frequency 1
    -22.0
    """
    # Table 1 values from Rodrigues & Taylor (2012)
    # c-bar values for constant only (model=1)
    cbar_constant = {
        0: -7.00,
        1: -12.25,
        2: -8.25,
        3: -7.75,
        4: -7.50,
        5: -7.25
    }
    
    # c-bar values for constant and trend (model=2)
    cbar_trend = {
        0: -13.50,
        1: -22.00,
        2: -16.25,
        3: -14.75,
        4: -14.25,
        5: -14.00
    }
    
    if model == 1:
        if k not in cbar_constant:
            raise ValueError(f"Invalid k={k} for model=1. Valid values: 0-5")
        return cbar_constant[k]
    elif model == 2:
        if k not in cbar_trend:
            raise ValueError(f"Invalid k={k} for model=2. Valid values: 0-5")
        return cbar_trend[k]
    else:
        raise ValueError(f"Invalid model={model}. Use 1 (constant) or 2 (constant+trend)")


def get_cbar_multiple(model: int, frequencies: Union[List[int], Tuple[int, ...]]) -> float:
    """
    Get the local GLS de-trending parameter for multiple Fourier frequencies.
    
    Returns values from Table 1 of Rodrigues & Taylor (2012) for cumulative
    Fourier frequencies.
    
    Parameters
    ----------
    model : int
        1 = Constant only
        2 = Constant and trend
    frequencies : list or tuple
        Tuple of frequencies, e.g., (1, 2) or (1, 2, 3, 4, 5)
    
    Returns
    -------
    float
        c-bar parameter value
    
    Notes
    -----
    From Table 1 (Rodrigues & Taylor, 2012, p. 4):
    
    frequencies    c-bar_kappa   c-bar_tau
    ----------------------------------------
    (1, 2)         -16.25        -30.00
    (1, 2, 3)      -19.50        -36.25
    (1, 2, 3, 4)   -21.75        -42.50
    (1, 2, 3, 4, 5) -24.75       -46.75
    """
    frequencies = tuple(sorted(frequencies))
    
    # Multiple frequency c-bar values from Table 1
    cbar_multiple_constant = {
        (1, 2): -16.25,
        (1, 2, 3): -19.50,
        (1, 2, 3, 4): -21.75,
        (1, 2, 3, 4, 5): -24.75
    }
    
    cbar_multiple_trend = {
        (1, 2): -30.00,
        (1, 2, 3): -36.25,
        (1, 2, 3, 4): -42.50,
        (1, 2, 3, 4, 5): -46.75
    }
    
    if model == 1:
        if frequencies not in cbar_multiple_constant:
            raise ValueError(f"No c-bar value for frequencies={frequencies}")
        return cbar_multiple_constant[frequencies]
    elif model == 2:
        if frequencies not in cbar_multiple_trend:
            raise ValueError(f"No c-bar value for frequencies={frequencies}")
        return cbar_multiple_trend[frequencies]
    else:
        raise ValueError(f"Invalid model={model}. Use 1 or 2")


def get_fourier_gls_critical_values(T: int, model: int) -> np.ndarray:
    """
    Get critical values for Fourier GLS unit root tests (single frequency).
    
    Returns values from Table 2 of Rodrigues & Taylor (2012).
    Critical values are provided for frequencies k = 1, 2, 3, 4, 5.
    
    Parameters
    ----------
    T : int
        Sample size
    model : int
        1 = Constant only (t^{ERS}_f^kappa)
        2 = Constant and trend (t^{ERS}_f^tau)
    
    Returns
    -------
    np.ndarray
        (5 x 3) array of critical values
        Rows: k = 1, 2, 3, 4, 5
        Columns: 1%, 5%, 10% significance levels
    
    Notes
    -----
    From Table 2 (Rodrigues & Taylor, 2012, pp. 6-7):
    
    The critical values depend on sample size:
    - T <= 150: small sample values
    - 151 < T <= 350: medium sample values  
    - T > 350: large sample values
    
    Examples
    --------
    >>> cv = get_fourier_gls_critical_values(100, 1)
    >>> cv[0, :]  # k=1, all significance levels
    array([-3.911, -3.294, -2.328])
    """
    # Critical values from Table 2 of Rodrigues & Taylor (2012)
    
    if model == 1:  # Constant only (t^{ERS}_f^kappa)
        if T <= 150:
            # T = 100 values from Table 2
            crit = np.array([
                [-3.911, -3.294, -2.328],  # k = 1
                [-3.298, -2.601, -2.187],  # k = 2
                [-3.131, -2.359, -2.005],  # k = 3
                [-2.934, -2.256, -1.918],  # k = 4
                [-2.888, -2.200, -1.880]   # k = 5
            ])
        elif 151 < T <= 350:
            # T = 200 values from Table 2
            crit = np.array([
                [-3.780, -3.176, -2.828],  # k = 1
                [-3.278, -2.473, -2.099],  # k = 2
                [-2.989, -2.226, -1.896],  # k = 3
                [-2.884, -2.179, -1.830],  # k = 4
                [-2.840, -2.120, -1.787]   # k = 5
            ])
        else:  # T > 350
            # T = 1000 values from Table 2
            crit = np.array([
                [-3.637, -3.017, -2.661],  # k = 1
                [-3.074, -2.377, -1.990],  # k = 2
                [-2.916, -2.175, -1.808],  # k = 3
                [-2.773, -2.079, -1.732],  # k = 4
                [-2.745, -2.022, -1.695]   # k = 5
            ])
            
    elif model == 2:  # Constant and trend (t^{ERS}_f^tau)
        if T <= 150:
            # T = 100 values from Table 2
            crit = np.array([
                [-4.771, -4.175, -3.879],  # k = 1
                [-4.278, -3.647, -3.316],  # k = 2
                [-4.044, -3.367, -3.037],  # k = 3
                [-3.920, -3.232, -2.902],  # k = 4
                [-3.797, -3.149, -2.831]   # k = 5
            ])
        elif 151 < T <= 350:
            # T = 200 values from Table 2
            crit = np.array([
                [-4.593, -4.041, -3.749],  # k = 1
                [-4.191, -3.569, -3.228],  # k = 2
                [-3.993, -3.300, -2.950],  # k = 3
                [-3.852, -3.174, -2.852],  # k = 4
                [-3.749, -3.075, -2.761]   # k = 5
            ])
        else:  # T > 350
            # T = 1000 values from Table 2
            crit = np.array([
                [-4.462, -3.917, -3.651],  # k = 1
                [-4.073, -3.438, -3.108],  # k = 2
                [-3.822, -3.220, -2.868],  # k = 3
                [-3.701, -3.092, -2.758],  # k = 4
                [-3.603, -3.012, -2.690]   # k = 5
            ])
    else:
        raise ValueError(f"Invalid model={model}. Use 1 (constant) or 2 (constant+trend)")
    
    return crit


def get_fourier_gls_critical_values_multiple(T: int, model: int) -> Dict[Tuple[int, ...], np.ndarray]:
    """
    Get critical values for multiple frequency Fourier GLS tests.
    
    Returns values from Table 3 of Rodrigues & Taylor (2012).
    
    Parameters
    ----------
    T : int
        Sample size
    model : int
        1 = Constant only
        2 = Constant and trend
    
    Returns
    -------
    dict
        Dictionary mapping frequency tuples to critical value arrays.
        Each array is (1 x 3) with 1%, 5%, 10% values.
    
    Notes
    -----
    From Table 3 (Rodrigues & Taylor, 2012, p. 8):
    
    Available frequency combinations:
    - (1, 2)
    - (1, 2, 3)
    - (1, 2, 3, 4)
    - (1, 2, 3, 4, 5)
    """
    crit_dict = {}
    
    if model == 1:  # Constant only (t^{ERS}_f^kappa)
        if T <= 150:
            crit_dict = {
                (1, 2): np.array([-4.833, -4.139, -3.757]),
                (1, 2, 3): np.array([-5.577, -4.835, -4.478]),
                (1, 2, 3, 4): np.array([-6.221, -5.517, -5.104]),
                (1, 2, 3, 4, 5): np.array([-6.920, -6.127, -5.754])
            }
        elif 151 < T <= 350:
            crit_dict = {
                (1, 2): np.array([-4.604, -3.958, -3.596]),
                (1, 2, 3): np.array([-5.247, -4.595, -4.230]),
                (1, 2, 3, 4): np.array([-5.853, -5.174, -4.784]),
                (1, 2, 3, 4, 5): np.array([-6.411, -5.746, -5.328])
            }
        else:
            crit_dict = {
                (1, 2): np.array([-4.357, -3.759, -3.373]),
                (1, 2, 3): np.array([-5.038, -4.361, -3.976]),
                (1, 2, 3, 4): np.array([-5.607, -4.875, -4.474]),
                (1, 2, 3, 4, 5): np.array([-6.043, -5.377, -4.963])
            }
            
    elif model == 2:  # Constant and trend (t^{ERS}_f^tau)
        if T <= 150:
            crit_dict = {
                (1, 2): np.array([-5.652, -5.052, -4.747]),
                (1, 2, 3): np.array([-6.438, -5.806, -5.501]),
                (1, 2, 3, 4): np.array([-7.141, -6.528, -6.204]),
                (1, 2, 3, 4, 5): np.array([-7.821, -7.171, -6.852])
            }
        elif 151 < T <= 350:
            crit_dict = {
                (1, 2): np.array([-5.410, -4.832, -4.545]),
                (1, 2, 3): np.array([-6.125, -5.515, -5.228]),
                (1, 2, 3, 4): np.array([-6.735, -6.162, -5.872]),
                (1, 2, 3, 4, 5): np.array([-7.295, -6.721, -6.435])
            }
        else:
            crit_dict = {
                (1, 2): np.array([-5.256, -4.693, -4.412]),
                (1, 2, 3): np.array([-5.917, -5.356, -5.077]),
                (1, 2, 3, 4): np.array([-6.438, -5.927, -5.650]),
                (1, 2, 3, 4, 5): np.array([-6.897, -6.391, -6.148])
            }
    else:
        raise ValueError(f"Invalid model={model}. Use 1 or 2")
    
    return crit_dict


def get_df_critical_values(T: int, model: int) -> np.ndarray:
    """
    Get critical values for Fourier DF (OLS de-trended) unit root tests.
    
    Returns values from Table 2 of Rodrigues & Taylor (2012).
    These correspond to t^{DF}_f^tau tests.
    
    Parameters
    ----------
    T : int
        Sample size
    model : int
        1 = Constant only (t^{DF}_f^kappa)
        2 = Constant and trend (t^{DF}_f^tau)
    
    Returns
    -------
    np.ndarray
        (5 x 3) array of critical values
        Rows: k = 1, 2, 3, 4, 5
        Columns: 1%, 5%, 10% significance levels
    """
    if model == 1:  # Constant only
        if T <= 150:
            crit = np.array([
                [-4.470, -3.862, -3.531],  # k = 1
                [-3.914, -3.267, -2.907],  # k = 2
                [-3.725, -3.068, -2.718],  # k = 3
                [-3.632, -2.965, -2.637],  # k = 4
                [-3.546, -2.926, -2.611]   # k = 5
            ])
        elif 151 < T <= 350:
            crit = np.array([
                [-4.381, -3.811, -3.495],
                [-3.956, -3.265, -2.902],
                [-3.745, -3.054, -2.712],
                [-3.621, -2.974, -2.650],
                [-3.590, -2.932, -2.613]
            ])
        else:
            crit = np.array([
                [-4.367, -3.764, -3.467],
                [-3.836, -3.260, -2.912],
                [-3.667, -3.064, -2.712],
                [-3.608, -2.976, -2.664],
                [-3.554, -2.926, -2.611]
            ])
            
    elif model == 2:  # Constant and trend
        if T <= 150:
            crit = np.array([
                [-4.988, -4.377, -4.073],  # k = 1
                [-4.662, -3.994, -3.688],  # k = 2
                [-4.413, -3.775, -3.449],  # k = 3
                [-4.281, -3.638, -3.283],  # k = 4
                [-4.205, -3.535, -3.229]   # k = 5
            ])
        elif 151 < T <= 350:
            crit = np.array([
                [-4.863, -4.318, -4.016],
                [-4.639, -4.055, -3.694],
                [-4.437, -3.781, -3.450],
                [-4.278, -3.677, -3.333],
                [-4.229, -3.586, -3.258]
            ])
        else:
            crit = np.array([
                [-4.844, -4.268, -4.008],
                [-4.562, -3.979, -3.666],
                [-4.340, -3.757, -3.419],
                [-4.219, -3.616, -3.293],
                [-4.159, -3.558, -3.244]
            ])
    else:
        raise ValueError(f"Invalid model={model}")
    
    return crit


def get_lm_critical_values(T: int, model: int = 2) -> np.ndarray:
    """
    Get critical values for Fourier LM unit root tests.
    
    Returns values from Table 2 of Rodrigues & Taylor (2012).
    Note: LM test only available for model=2 (constant and trend).
    
    Parameters
    ----------
    T : int
        Sample size
    model : int
        2 = Constant and trend (only valid option for LM)
    
    Returns
    -------
    np.ndarray
        (5 x 3) array of critical values
    """
    if model != 2:
        raise ValueError("LM test only available for model=2 (constant and trend)")
    
    if T <= 150:
        crit = np.array([
            [-4.689, -4.137, -3.830],  # k = 1
            [-4.184, -3.545, -3.218],  # k = 2
            [-4.024, -3.304, -2.976],  # k = 3
            [-3.846, -3.185, -2.880],  # k = 4
            [-3.762, -3.122, -2.815]   # k = 5
        ])
    elif 151 < T <= 350:
        crit = np.array([
            [-4.618, -4.077, -3.800],
            [-4.228, -3.577, -3.234],
            [-4.012, -3.335, -2.969],
            [-3.901, -3.221, -2.884],
            [-3.782, -3.146, -2.827]
        ])
    else:
        crit = np.array([
            [-4.559, -4.032, -3.764],
            [-4.142, -3.540, -3.200],
            [-3.925, -3.298, -2.960],
            [-3.817, -3.195, -2.872],
            [-3.752, -3.125, -2.822]
        ])
    
    return crit


def _gls_detrend_for_simulation(y: np.ndarray, z: np.ndarray, cbar: float) -> np.ndarray:
    """
    GLS detrending for critical value simulation.
    
    Internal function used by simulate_critical_values.
    """
    T = len(y)
    a = 1 + cbar / T
    
    # Quasi-difference transformation
    ya = np.zeros(T)
    za = np.zeros((T, z.shape[1]))
    
    ya[0] = y[0]
    za[0, :] = z[0, :]
    
    ya[1:] = y[1:] - a * y[:-1]
    za[1:, :] = z[1:, :] - a * z[:-1, :]
    
    # Detrending regression
    bhat = np.linalg.lstsq(za, ya, rcond=None)[0]
    
    return y - z @ bhat


def simulate_critical_values(T: int, model: int, k: int, 
                              n_simulations: int = 10000,
                              seed: Optional[int] = None) -> np.ndarray:
    """
    Simulate critical values for Fourier GLS unit root test.
    
    Generates critical values by Monte Carlo simulation under the
    null hypothesis of a unit root, following the methodology in
    Rodrigues & Taylor (2012).
    
    Parameters
    ----------
    T : int
        Sample size
    model : int
        1 = Constant only
        2 = Constant and trend
    k : int
        Fourier frequency (1-5)
    n_simulations : int, optional
        Number of Monte Carlo replications, by default 10000
    seed : int, optional
        Random seed for reproducibility
    
    Returns
    -------
    np.ndarray
        Array of [1%, 5%, 10%] critical values
    
    Notes
    -----
    The DGP under H0 is:
        x_t = x_{t-1} + u_t,  u_t ~ NIID(0, 1)
    
    with x_0 = 0 (the test is exact similar with respect to x_0).
    
    This follows the simulation design in Rodrigues & Taylor (2012, p. 6).
    
    Examples
    --------
    >>> cv = simulate_critical_values(100, 2, 1, n_simulations=5000, seed=42)
    >>> print(f"5% CV: {cv[1]:.3f}")
    """
    if seed is not None:
        np.random.seed(seed)
    
    cbar = get_cbar(model, k)
    
    statistics = np.zeros(n_simulations)
    
    for sim in range(n_simulations):
        # Generate random walk under H0: x_t = x_{t-1} + u_t
        u = np.random.randn(T)
        x = np.cumsum(u)  # This gives x_0 = u_0, x_1 = u_0 + u_1, etc.
        
        # Build regressor matrix with Fourier terms
        sink, cosk = get_fourier_terms(T, k)
        
        if model == 1:
            z = np.column_stack([np.ones(T), sink, cosk])
        else:
            z = np.column_stack([np.ones(T), np.arange(1, T + 1), sink, cosk])
        
        # GLS detrending
        ygls = _gls_detrend_for_simulation(x, z, cbar)
        
        # ADF regression on detrended series (no augmentation under H0 with iid errors)
        dy = ygls[1:] - ygls[:-1]
        y_lag = ygls[:-1]
        
        # OLS regression: dy = rho * y_lag + error
        _, _, sig2, se, _ = ols(dy, y_lag.reshape(-1, 1))
        b = np.linalg.lstsq(y_lag.reshape(-1, 1), dy, rcond=None)[0]
        
        # t-statistic
        statistics[sim] = b[0] / se[0]
    
    # Compute percentiles (1%, 5%, 10%)
    cv = np.percentile(statistics, [1, 5, 10])
    
    return cv


def simulate_all_critical_values(T: int, model: int,
                                  n_simulations: int = 10000,
                                  seed: Optional[int] = None) -> np.ndarray:
    """
    Simulate critical values for all frequencies k = 1, ..., 5.
    
    Parameters
    ----------
    T : int
        Sample size
    model : int
        1 = Constant only
        2 = Constant and trend
    n_simulations : int, optional
        Number of Monte Carlo replications
    seed : int, optional
        Random seed for reproducibility
    
    Returns
    -------
    np.ndarray
        (5 x 3) array of critical values
        Rows: k = 1, 2, 3, 4, 5
        Columns: 1%, 5%, 10%
    """
    results = np.zeros((5, 3))
    
    for k in range(1, 6):
        if seed is not None:
            np.random.seed(seed + k)
        results[k - 1, :] = simulate_critical_values(
            T, model, k, n_simulations, seed=None if seed is None else seed + k
        )
    
    return results


def compare_critical_values(T: int, model: int, 
                             n_simulations: int = 10000,
                             seed: int = 42) -> None:
    """
    Compare simulated critical values with tabulated values.
    
    Useful for verification of the implementation.
    
    Parameters
    ----------
    T : int
        Sample size
    model : int
        1 = Constant only
        2 = Constant and trend
    n_simulations : int, optional
        Number of Monte Carlo replications
    seed : int, optional
        Random seed
    """
    print(f"\nComparing critical values for T={T}, model={model}")
    print("=" * 60)
    
    tabulated = get_fourier_gls_critical_values(T, model)
    simulated = simulate_all_critical_values(T, model, n_simulations, seed)
    
    print(f"{'k':<4}{'Tabulated (1%, 5%, 10%)':<35}{'Simulated (1%, 5%, 10%)':<35}")
    print("-" * 60)
    
    for k in range(1, 6):
        tab_str = f"[{tabulated[k-1, 0]:.3f}, {tabulated[k-1, 1]:.3f}, {tabulated[k-1, 2]:.3f}]"
        sim_str = f"[{simulated[k-1, 0]:.3f}, {simulated[k-1, 1]:.3f}, {simulated[k-1, 2]:.3f}]"
        print(f"{k:<4}{tab_str:<35}{sim_str:<35}")
