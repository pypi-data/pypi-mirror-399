"""
Tests for Fourier GLS Unit Root Tests.

This test module verifies:
1. Compatibility with original GAUSS code
2. Consistency with Rodrigues & Taylor (2012) paper
3. Correct critical values from Tables 1-3
4. Proper handling of edge cases

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np
import pytest
from fourier_gls import (
    fourier_gls,
    fourier_gls_f_test,
    gls_detrend,
    get_cbar,
    get_fourier_gls_critical_values,
    diff,
    lagn,
    trimr,
    get_fourier_terms,
    ols,
    get_lag_by_ic,
)


class TestCriticalValues:
    """Test critical values match Table 1 and Table 2 from the paper."""
    
    def test_cbar_constant_model(self):
        """Test c-bar values for constant model (Table 1)."""
        # From Table 1, column c-bar_kappa
        expected = {
            0: -7.00,
            1: -12.25,
            2: -8.25,
            3: -7.75,
            4: -7.50,
            5: -7.25
        }
        for k, expected_cbar in expected.items():
            result = get_cbar(1, k)
            assert np.isclose(result, expected_cbar), \
                f"c-bar for model=1, k={k}: expected {expected_cbar}, got {result}"
    
    def test_cbar_trend_model(self):
        """Test c-bar values for trend model (Table 1)."""
        # From Table 1, column c-bar_tau
        expected = {
            0: -13.50,
            1: -22.00,
            2: -16.25,
            3: -14.75,
            4: -14.25,
            5: -14.00
        }
        for k, expected_cbar in expected.items():
            result = get_cbar(2, k)
            assert np.isclose(result, expected_cbar), \
                f"c-bar for model=2, k={k}: expected {expected_cbar}, got {result}"
    
    def test_critical_values_table2_constant_T100(self):
        """Test critical values for constant model, T=100 (Table 2)."""
        cv = get_fourier_gls_critical_values(100, 1)
        
        # Expected values from Table 2
        expected = np.array([
            [-3.911, -3.294, -2.328],  # k = 1
            [-3.298, -2.601, -2.187],  # k = 2
            [-3.131, -2.359, -2.005],  # k = 3
            [-2.934, -2.256, -1.918],  # k = 4
            [-2.888, -2.200, -1.880]   # k = 5
        ])
        
        np.testing.assert_array_almost_equal(cv, expected, decimal=3)
    
    def test_critical_values_table2_trend_T100(self):
        """Test critical values for trend model, T=100 (Table 2)."""
        cv = get_fourier_gls_critical_values(100, 2)
        
        expected = np.array([
            [-4.771, -4.175, -3.879],
            [-4.278, -3.647, -3.316],
            [-4.044, -3.367, -3.037],
            [-3.920, -3.232, -2.902],
            [-3.797, -3.149, -2.831]
        ])
        
        np.testing.assert_array_almost_equal(cv, expected, decimal=3)
    
    def test_critical_values_table2_trend_T200(self):
        """Test critical values for trend model, T=200 (Table 2)."""
        cv = get_fourier_gls_critical_values(200, 2)
        
        expected = np.array([
            [-4.593, -4.041, -3.749],
            [-4.191, -3.569, -3.228],
            [-3.993, -3.300, -2.950],
            [-3.852, -3.174, -2.852],
            [-3.749, -3.075, -2.761]
        ])
        
        np.testing.assert_array_almost_equal(cv, expected, decimal=3)
    
    def test_critical_values_table2_trend_T1000(self):
        """Test critical values for trend model, T=1000 (Table 2)."""
        cv = get_fourier_gls_critical_values(1000, 2)
        
        expected = np.array([
            [-4.462, -3.917, -3.651],
            [-4.073, -3.438, -3.108],
            [-3.822, -3.220, -2.868],
            [-3.701, -3.092, -2.758],
            [-3.603, -3.012, -2.690]
        ])
        
        np.testing.assert_array_almost_equal(cv, expected, decimal=3)


class TestUtilityFunctions:
    """Test utility functions for correct GAUSS-like behavior."""
    
    def test_diff(self):
        """Test differencing function."""
        y = np.array([1.0, 3.0, 6.0, 10.0, 15.0])
        result = diff(y, 1)
        
        assert np.isnan(result[0])
        np.testing.assert_array_almost_equal(result[1:], [2., 3., 4., 5.])
    
    def test_lagn_single(self):
        """Test single lag creation."""
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = lagn(y, 1)
        
        assert np.isnan(result[0])
        np.testing.assert_array_almost_equal(result[1:], [1., 2., 3., 4.])
    
    def test_lagn_multiple(self):
        """Test multiple lag creation."""
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = lagn(y, np.array([1, 2]))
        
        assert result.shape == (5, 2)
        assert np.isnan(result[0, 0])
        assert np.isnan(result[0, 1])
        assert np.isnan(result[1, 1])
    
    def test_trimr(self):
        """Test trimming function."""
        x = np.array([1, 2, 3, 4, 5])
        result = trimr(x, 1, 1)
        np.testing.assert_array_equal(result, [2, 3, 4])
        
        result = trimr(x, 2, 0)
        np.testing.assert_array_equal(result, [3, 4, 5])
    
    def test_fourier_terms(self):
        """Test Fourier term generation."""
        T = 100
        k = 1
        sink, cosk = get_fourier_terms(T, k)
        
        assert len(sink) == T
        assert len(cosk) == T
        
        # Check values at key points
        t = np.arange(1, T + 1)
        expected_sin = np.sin(2 * np.pi * k * t / T)
        expected_cos = np.cos(2 * np.pi * k * t / T)
        
        np.testing.assert_array_almost_equal(sink, expected_sin)
        np.testing.assert_array_almost_equal(cosk, expected_cos)
    
    def test_ols(self):
        """Test OLS estimation."""
        np.random.seed(42)
        n = 100
        X = np.column_stack([np.ones(n), np.random.randn(n)])
        true_b = np.array([1.0, 2.0])
        y = X @ true_b + 0.1 * np.random.randn(n)
        
        b, e, sig2, se, ssr = ols(y, X)
        
        assert len(b) == 2
        assert len(e) == n
        assert len(se) == 2
        assert sig2 > 0
        assert ssr > 0
        
        # Check coefficients are close to true values
        np.testing.assert_array_almost_equal(b, true_b, decimal=1)
    
    def test_get_lag_by_ic(self):
        """Test lag selection by information criterion."""
        pmax = 4
        
        # Create mock IC values where p=2 is optimal
        aic = np.array([10.0, 8.0, 5.0, 6.0, 7.0])  # Min at p=2
        sic = np.array([10.0, 8.0, 5.0, 6.0, 7.0])
        tstat = np.array([1.0, 1.5, 2.0, 1.8, 1.2])
        
        # Test AIC
        result = get_lag_by_ic(1, pmax, aic, sic, tstat)
        assert result == 3  # 1-indexed, so min at index 2 -> returns 3
        
        # Test SIC
        result = get_lag_by_ic(2, pmax, aic, sic, tstat)
        assert result == 3


class TestGLSDetrend:
    """Test GLS detrending function."""
    
    def test_gls_detrend_basic(self):
        """Test basic GLS detrending."""
        np.random.seed(42)
        T = 100
        y = np.cumsum(np.random.randn(T))
        
        # Build regressor matrix
        sink, cosk = get_fourier_terms(T, 1)
        z = np.column_stack([np.ones(T), sink, cosk])
        
        cbar = get_cbar(1, 1)
        ygls = gls_detrend(y, z, cbar)
        
        assert len(ygls) == T
        assert not np.any(np.isnan(ygls))
    
    def test_gls_detrend_with_ssr(self):
        """Test GLS detrending with SSR return."""
        np.random.seed(42)
        T = 100
        y = np.cumsum(np.random.randn(T))
        
        sink, cosk = get_fourier_terms(T, 1)
        z = np.column_stack([np.ones(T), np.arange(1, T + 1), sink, cosk])
        
        cbar = get_cbar(2, 1)
        ygls, ssr = gls_detrend(y, z, cbar, return_ssr=True)
        
        assert len(ygls) == T
        assert ssr > 0


class TestFourierGLS:
    """Test main Fourier GLS function."""
    
    def test_fourier_gls_unit_root(self):
        """Test Fourier GLS with unit root DGP."""
        np.random.seed(42)
        T = 200
        
        # Generate random walk (unit root)
        y = np.cumsum(np.random.randn(T))
        
        result = fourier_gls(y, model=2, verbose=False)
        
        assert hasattr(result, 'statistic')
        assert hasattr(result, 'frequency')
        assert hasattr(result, 'lags')
        assert hasattr(result, 'critical_values')
        assert 1 <= result.frequency <= 5
        assert result.lags >= 0
        assert len(result.critical_values) == 3
    
    def test_fourier_gls_stationary(self):
        """Test Fourier GLS with stationary DGP."""
        np.random.seed(42)
        T = 200
        
        # Generate stationary AR(1)
        rho = 0.5
        y = np.zeros(T)
        for t in range(1, T):
            y[t] = rho * y[t-1] + np.random.randn()
        
        result = fourier_gls(y, model=2, verbose=False)
        
        # Should reject unit root more often for stationary data
        assert result.statistic < 0  # t-stat should be negative
    
    def test_fourier_gls_models(self):
        """Test both model specifications."""
        np.random.seed(42)
        T = 100
        y = np.cumsum(np.random.randn(T))
        
        # Constant model
        result1 = fourier_gls(y, model=1, verbose=False)
        assert result1.model == 1
        
        # Trend model
        result2 = fourier_gls(y, model=2, verbose=False)
        assert result2.model == 2
    
    def test_fourier_gls_pmax_options(self):
        """Test different pmax values."""
        np.random.seed(42)
        T = 100
        y = np.cumsum(np.random.randn(T))
        
        for pmax in [0, 4, 8, 12]:
            result = fourier_gls(y, model=2, pmax=pmax, verbose=False)
            assert result.lags <= pmax
    
    def test_fourier_gls_ic_options(self):
        """Test different information criteria."""
        np.random.seed(42)
        T = 100
        y = np.cumsum(np.random.randn(T))
        
        for ic in [1, 2, 3]:
            result = fourier_gls(y, model=2, ic=ic, verbose=False)
            assert result.statistic is not None


class TestFourierGLSFTest:
    """Test F-test for Fourier terms."""
    
    def test_f_test_basic(self):
        """Test basic F-test functionality."""
        np.random.seed(42)
        T = 100
        y = np.cumsum(np.random.randn(T))
        
        result = fourier_gls_f_test(y, model=2, k=1, p=0, verbose=False)
        
        assert hasattr(result, 'f_statistic')
        assert hasattr(result, 'critical_values')
        assert result.f_statistic > 0
        assert len(result.critical_values) == 3


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_model(self):
        """Test error on invalid model specification."""
        y = np.random.randn(100)
        
        with pytest.raises(ValueError):
            fourier_gls(y, model=3, verbose=False)
    
    def test_invalid_fmax(self):
        """Test error on invalid fmax."""
        y = np.random.randn(100)
        
        with pytest.raises(ValueError):
            fourier_gls(y, model=2, fmax=6, verbose=False)
    
    def test_invalid_ic(self):
        """Test error on invalid information criterion."""
        y = np.random.randn(100)
        
        with pytest.raises(ValueError):
            fourier_gls(y, model=2, ic=4, verbose=False)
    
    def test_missing_values(self):
        """Test error on missing values."""
        y = np.random.randn(100)
        y[50] = np.nan
        
        with pytest.raises(ValueError):
            fourier_gls(y, model=2, verbose=False)
    
    def test_small_sample(self):
        """Test with small sample size."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(50))
        
        result = fourier_gls(y, model=1, pmax=4, verbose=False)
        assert result.statistic is not None


class TestReproducibility:
    """Test reproducibility of results."""
    
    def test_deterministic_results(self):
        """Test that results are deterministic."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        
        result1 = fourier_gls(y, model=2, verbose=False)
        result2 = fourier_gls(y, model=2, verbose=False)
        
        assert result1.statistic == result2.statistic
        assert result1.frequency == result2.frequency
        assert result1.lags == result2.lags


class TestOutputFormat:
    """Test output formatting."""
    
    def test_result_to_dict(self):
        """Test conversion to dictionary."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        result = fourier_gls(y, model=2, verbose=False)
        d = result.to_dict()
        
        assert 'statistic' in d
        assert 'frequency' in d
        assert 'lags' in d
        assert 'critical_values' in d
        assert '1%' in d['critical_values']
        assert '5%' in d['critical_values']
        assert '10%' in d['critical_values']
    
    def test_result_summary(self):
        """Test summary string generation."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        result = fourier_gls(y, model=2, verbose=False)
        summary = result.summary()
        
        assert 'Fourier GLS' in summary
        assert 'Test Statistic' in summary
        assert 'Critical Values' in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
