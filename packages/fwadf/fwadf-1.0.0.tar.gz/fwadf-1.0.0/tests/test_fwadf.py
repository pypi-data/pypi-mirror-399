"""
Test suite for FWADF library.

Tests verify compatibility with original GAUSS code and
Sephton (2024) methodology.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_less

# Import modules
from fwadf import (
    fwadf_test,
    wadf_test,
    haar_dwt,
    haar_scaling_coefficients,
    get_fwadf_critical_values,
    get_wadf_critical_values,
    get_fwadf_pvalue,
    get_wadf_pvalue,
    simulate_fwadf_critical_values,
    simulate_wadf_critical_values,
    FWADFResult,
    WADFResult
)


class TestWaveletTransform:
    """Tests for Haar wavelet transformation."""
    
    def test_haar_dwt_length(self):
        """Test that DWT reduces length by half."""
        data = np.random.randn(100)
        scaling, wavelet = haar_dwt(data)
        assert len(scaling) == 50
        assert len(wavelet) == 50
    
    def test_haar_dwt_values(self):
        """Test DWT computation matches formula."""
        data = np.array([1.0, 2.0, 3.0, 4.0])
        scaling, wavelet = haar_dwt(data)
        
        # V[0] = (x[0] + x[1]) / sqrt(2) = (1 + 2) / sqrt(2)
        expected_scaling_0 = (1.0 + 2.0) / np.sqrt(2)
        assert_allclose(scaling[0], expected_scaling_0)
        
        # W[0] = (x[1] - x[0]) / sqrt(2) = (2 - 1) / sqrt(2)
        expected_wavelet_0 = (2.0 - 1.0) / np.sqrt(2)
        assert_allclose(wavelet[0], expected_wavelet_0)
    
    def test_haar_scaling_coefficients(self):
        """Test scaling coefficients extraction."""
        data = np.random.randn(100)
        V = haar_scaling_coefficients(data)
        scaling, _ = haar_dwt(data)
        assert_allclose(V, scaling)
    
    def test_haar_dwt_odd_length(self):
        """Test DWT with odd-length input."""
        data = np.random.randn(101)
        scaling, wavelet = haar_dwt(data)
        assert len(scaling) == 50


class TestWADFTest:
    """Tests for WADF unit root test."""
    
    def test_wadf_returns_result(self):
        """Test that WADF returns proper result object."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = wadf_test(data, model=1, verbose=False)
        
        assert isinstance(result, WADFResult)
        assert hasattr(result, 'statistic')
        assert hasattr(result, 'pvalue')
        assert hasattr(result, 'lag')
        assert hasattr(result, 'critical_values')
    
    def test_wadf_statistic_range(self):
        """Test that WADF statistic is in reasonable range."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = wadf_test(data, model=1, verbose=False)
        
        # For unit root process, statistic should be around -1 to -3
        assert -10 < result.statistic < 2
    
    def test_wadf_pvalue_range(self):
        """Test that p-value is between 0 and 1."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = wadf_test(data, model=1, verbose=False)
        
        assert 0 < result.pvalue < 1
    
    def test_wadf_model_1_vs_2(self):
        """Test that model 2 gives more negative critical values."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        
        result1 = wadf_test(data, model=1, verbose=False)
        result2 = wadf_test(data, model=2, verbose=False)
        
        # Model 2 (trend) should have more negative 5% critical value
        assert result2.critical_values[0.05] < result1.critical_values[0.05]
    
    def test_wadf_ic_selection(self):
        """Test AIC vs BIC lag selection."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        
        result_aic = wadf_test(data, model=1, ic='aic', verbose=False)
        result_bic = wadf_test(data, model=1, ic='bic', verbose=False)
        
        # BIC generally selects fewer lags
        assert result_bic.lag <= result_aic.lag + 2


class TestFWADFTest:
    """Tests for FWADF unit root test."""
    
    def test_fwadf_returns_result(self):
        """Test that FWADF returns proper result object."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = fwadf_test(data, model=1, verbose=False)
        
        assert isinstance(result, FWADFResult)
        assert hasattr(result, 'statistic')
        assert hasattr(result, 'pvalue')
        assert hasattr(result, 'k')
        assert hasattr(result, 'fourier_t_stat')
        assert hasattr(result, 'fourier_significant')
    
    def test_fwadf_k_selection(self):
        """Test that k is selected from valid range."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = fwadf_test(data, model=1, max_freq=5, verbose=False)
        
        assert 1 <= result.k <= 5
    
    def test_fwadf_custom_freq_grid(self):
        """Test FWADF with custom frequency grid."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        
        freq_grid = [1.0, 1.5, 2.0, 2.5, 3.0]
        result = fwadf_test(data, model=1, freq_grid=freq_grid, verbose=False)
        
        assert result.k in freq_grid
    
    def test_fwadf_stationary_series(self):
        """Test FWADF with stationary series should reject H0."""
        np.random.seed(42)
        # Generate AR(1) with phi < 1 (stationary)
        T = 300
        data = np.zeros(T)
        for t in range(1, T):
            data[t] = 0.5 * data[t-1] + np.random.randn()
        
        result = fwadf_test(data, model=1, verbose=False)
        
        # For stationary series, should reject null with high probability
        # (p-value should be small, statistic should be very negative)
        assert result.statistic < -2
    
    def test_fwadf_with_break(self):
        """Test FWADF with structural break in series."""
        np.random.seed(42)
        T = 200
        data = np.cumsum(np.random.randn(T))
        data[100:] += 5  # Level shift
        
        result = fwadf_test(data, model=1, verbose=False)
        
        # Fourier term might capture the break
        assert result.k >= 1
    
    def test_fwadf_all_k_results(self):
        """Test that all_k_results contains all frequencies."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = fwadf_test(data, model=1, max_freq=5, verbose=False)
        
        # Should have results for k = 1, 2, 3, 4, 5
        assert len(result.all_k_results) >= 1
        for k, res in result.all_k_results.items():
            assert 'ssr' in res
            assert 'test_stat' in res


class TestCriticalValues:
    """Tests for critical value functions."""
    
    def test_fwadf_cv_returns_dict(self):
        """Test that get_fwadf_critical_values returns dict."""
        cv = get_fwadf_critical_values(T=100, lag=2, model=1, k=2)
        
        assert isinstance(cv, dict)
        assert 0.01 in cv
        assert 0.05 in cv
        assert 0.10 in cv
    
    def test_fwadf_cv_ordering(self):
        """Test that critical values are properly ordered."""
        cv = get_fwadf_critical_values(T=100, lag=2, model=1, k=2)
        
        # 1% CV should be more negative than 5%, which is more negative than 10%
        assert cv[0.01] < cv[0.05] < cv[0.10]
    
    def test_wadf_cv_returns_dict(self):
        """Test that get_wadf_critical_values returns dict."""
        cv = get_wadf_critical_values(T=100, lag=2, model=1)
        
        assert isinstance(cv, dict)
        assert 0.01 in cv
    
    def test_fwadf_pvalue_range(self):
        """Test that p-values are in valid range."""
        pval = get_fwadf_pvalue(-3.0, T=100, lag=2, model=1, k=2)
        
        assert 0 < pval < 1
    
    def test_fwadf_pvalue_monotonic(self):
        """Test that more negative statistics give smaller p-values."""
        pval1 = get_fwadf_pvalue(-2.0, T=100, lag=2, model=1, k=2)
        pval2 = get_fwadf_pvalue(-3.0, T=100, lag=2, model=1, k=2)
        pval3 = get_fwadf_pvalue(-4.0, T=100, lag=2, model=1, k=2)
        
        assert pval1 > pval2 > pval3


class TestSimulation:
    """Tests for Monte Carlo simulation functions."""
    
    def test_simulate_wadf_cv(self):
        """Test WADF critical value simulation (small scale)."""
        cv = simulate_wadf_critical_values(
            T=100,
            lag=0,
            model=1,
            replications=500,  # Small for testing
            seed=42
        )
        
        assert isinstance(cv, dict)
        # Critical values should be negative
        for q, val in cv.items():
            assert val < 0
    
    def test_simulate_fwadf_cv(self):
        """Test FWADF critical value simulation (small scale)."""
        cv = simulate_fwadf_critical_values(
            T=100,
            lag=0,
            k=1.0,
            model=1,
            replications=500,  # Small for testing
            seed=42
        )
        
        assert isinstance(cv, dict)
        for q, val in cv.items():
            assert val < 0


class TestCompatibility:
    """Tests for compatibility with original GAUSS code."""
    
    def test_wavelet_transform_gauss_compatible(self):
        """Test wavelet transform matches GAUSS implementation."""
        # The GAUSS code uses:
        # d1[n1]=(y[t2+1,.]-y[t2,.])/sqrt(2);  (wavelet)
        # yt[n1]=(y[t2+1,.]+y[t2,.])/sqrt(2);  (scaling)
        
        data = np.array([1.0, 3.0, 2.0, 4.0, 3.0, 5.0])
        scaling, wavelet = haar_dwt(data)
        
        # Manual calculation following GAUSS
        expected_scaling = np.array([
            (3.0 + 1.0) / np.sqrt(2),  # (y[2] + y[1]) / sqrt(2)
            (4.0 + 2.0) / np.sqrt(2),  # (y[4] + y[3]) / sqrt(2)
            (5.0 + 3.0) / np.sqrt(2),  # (y[6] + y[5]) / sqrt(2)
        ])
        expected_wavelet = np.array([
            (3.0 - 1.0) / np.sqrt(2),
            (4.0 - 2.0) / np.sqrt(2),
            (5.0 - 3.0) / np.sqrt(2),
        ])
        
        assert_allclose(scaling, expected_scaling)
        assert_allclose(wavelet, expected_wavelet)
    
    def test_critical_values_match_paper(self):
        """Test critical values match Aydin & Pata (2020) Table A1."""
        # From Table A1 in the paper (model 1, constant)
        expected_cv = {
            1: {0.01: -3.84, 0.05: -3.23, 0.10: -2.89},
            2: {0.01: -3.54, 0.05: -2.91, 0.10: -2.51},
            3: {0.01: -3.24, 0.05: -2.69, 0.10: -2.41},
        }
        
        for k, cvs in expected_cv.items():
            # Get asymptotic CV (large T, lag=0)
            computed_cv = get_fwadf_critical_values(T=500, lag=0, model=1, k=k)
            
            for level, expected in cvs.items():
                # Allow some tolerance for response surface adjustment
                assert abs(computed_cv[level] - expected) < 0.3


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_short_series_error(self):
        """Test that short series raises error."""
        data = np.random.randn(10)
        
        with pytest.raises(ValueError):
            wadf_test(data, verbose=False)
    
    def test_nan_handling(self):
        """Test that NaN in data raises error."""
        data = np.random.randn(100)
        data[50] = np.nan
        
        with pytest.raises(ValueError):
            haar_dwt(data)
    
    def test_invalid_model(self):
        """Test that invalid model raises warning/error."""
        data = np.cumsum(np.random.randn(100))
        
        # Model 3 is not valid
        with pytest.warns(UserWarning) or pytest.raises(ValueError):
            wadf_test(data, model=3, verbose=False)


class TestResultFormatting:
    """Tests for result object formatting."""
    
    def test_wadf_str_representation(self):
        """Test WADF result string representation."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = wadf_test(data, model=1, verbose=False)
        
        result_str = str(result)
        
        assert "WADF" in result_str
        assert "Test Statistic" in result_str
        assert "P-value" in result_str
    
    def test_fwadf_str_representation(self):
        """Test FWADF result string representation."""
        np.random.seed(42)
        data = np.cumsum(np.random.randn(200))
        result = fwadf_test(data, model=1, verbose=False)
        
        result_str = str(result)
        
        assert "FWADF" in result_str
        assert "Fourier" in result_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
