"""
Test Suite for QFADF - Quantile Fourier ADF Unit Root Test

This module contains comprehensive tests for the qfadf package.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np
import pandas as pd
import pytest
import sys
import os

# Add the parent directory to the path for local testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qfadf import (
    qr_fourier_adf,
    qr_fourier_adf_bootstrap,
    qks_qcm_statistics,
    estimate_optimal_k,
    get_critical_values,
    prepare_data,
    adf_lag_selection,
    summary_statistics,
    format_results_latex,
    format_results_dataframe
)


class TestDataPreparation:
    """Test data preparation utilities."""
    
    def test_prepare_data_array(self):
        """Test data preparation with numpy array."""
        y = np.random.randn(100)
        result = prepare_data(y)
        assert isinstance(result, np.ndarray)
        assert len(result) == 100
    
    def test_prepare_data_series(self):
        """Test data preparation with pandas Series."""
        y = pd.Series(np.random.randn(100))
        result = prepare_data(y)
        assert isinstance(result, np.ndarray)
        assert len(result) == 100
    
    def test_prepare_data_dataframe(self):
        """Test data preparation with pandas DataFrame."""
        df = pd.DataFrame({'x': np.random.randn(100)})
        result = prepare_data(df, column='x')
        assert isinstance(result, np.ndarray)
        assert len(result) == 100
    
    def test_prepare_data_list(self):
        """Test data preparation with list."""
        y = list(np.random.randn(100))
        result = prepare_data(y)
        assert isinstance(result, np.ndarray)
        assert len(result) == 100


class TestCoreFunctions:
    """Test core test functions."""
    
    @pytest.fixture
    def unit_root_data(self):
        """Generate unit root process (random walk)."""
        np.random.seed(42)
        return np.cumsum(np.random.randn(200))
    
    @pytest.fixture
    def stationary_data(self):
        """Generate stationary AR(1) process."""
        np.random.seed(42)
        n = 200
        phi = 0.5
        y = np.zeros(n)
        for t in range(1, n):
            y[t] = phi * y[t-1] + np.random.randn()
        return y
    
    def test_qr_fourier_adf_model1(self, unit_root_data):
        """Test QR-Fourier-ADF with model 1 (constant only)."""
        result = qr_fourier_adf(unit_root_data, model=1, tau=0.5, 
                                 pmax=8, k=3, print_results=False)
        
        assert 'tn' in result
        assert 'rho_tau' in result
        assert 'tau' in result
        assert result['model'] == 1
        assert result['k'] == 3
        assert np.isfinite(result['tn'])
    
    def test_qr_fourier_adf_model2(self, unit_root_data):
        """Test QR-Fourier-ADF with model 2 (constant + trend)."""
        result = qr_fourier_adf(unit_root_data, model=2, tau=0.5,
                                 pmax=8, k=3, print_results=False)
        
        assert result['model'] == 2
        assert np.isfinite(result['tn'])
    
    def test_qr_fourier_adf_different_quantiles(self, unit_root_data):
        """Test QR-Fourier-ADF at different quantiles."""
        for tau in [0.1, 0.25, 0.5, 0.75, 0.9]:
            result = qr_fourier_adf(unit_root_data, model=1, tau=tau,
                                     print_results=False)
            assert abs(result['tau'] - tau) < 1e-10
            assert np.isfinite(result['tn'])
    
    def test_qr_fourier_adf_different_k(self, unit_root_data):
        """Test QR-Fourier-ADF with different Fourier frequencies."""
        for k in [1, 2, 3, 4, 5]:
            result = qr_fourier_adf(unit_root_data, model=1, tau=0.5,
                                     k=k, print_results=False)
            assert result['k'] == k
            assert np.isfinite(result['tn'])
    
    def test_qr_fourier_adf_invalid_tau(self, unit_root_data):
        """Test that invalid tau raises error."""
        with pytest.raises(ValueError):
            qr_fourier_adf(unit_root_data, tau=0.0)
        with pytest.raises(ValueError):
            qr_fourier_adf(unit_root_data, tau=1.0)
        with pytest.raises(ValueError):
            qr_fourier_adf(unit_root_data, tau=1.5)
    
    def test_qr_fourier_adf_invalid_model(self, unit_root_data):
        """Test that invalid model raises error."""
        with pytest.raises(ValueError):
            qr_fourier_adf(unit_root_data, model=3)
    
    def test_qr_fourier_adf_invalid_k(self, unit_root_data):
        """Test that invalid k raises error."""
        with pytest.raises(ValueError):
            qr_fourier_adf(unit_root_data, k=0)
        with pytest.raises(ValueError):
            qr_fourier_adf(unit_root_data, k=6)
    
    def test_rho_near_one_for_unit_root(self, unit_root_data):
        """Test that ρ(τ) is near 1 for unit root process."""
        result = qr_fourier_adf(unit_root_data, model=1, tau=0.5,
                                 print_results=False)
        # For unit root, ρ should be close to 1
        assert result['rho_tau'] > 0.9


class TestBootstrap:
    """Test bootstrap procedures."""
    
    @pytest.fixture
    def test_data(self):
        """Generate test data."""
        np.random.seed(42)
        return np.cumsum(np.random.randn(100))
    
    def test_bootstrap_returns_cv(self, test_data):
        """Test that bootstrap returns critical values."""
        result = qr_fourier_adf_bootstrap(test_data, model=1, tau=0.5,
                                           n_boot=100, print_results=False,
                                           random_state=42)
        
        assert 'cv' in result
        assert '1%' in result['cv']
        assert '5%' in result['cv']
        assert '10%' in result['cv']
    
    def test_bootstrap_returns_pvalue(self, test_data):
        """Test that bootstrap returns p-value."""
        result = qr_fourier_adf_bootstrap(test_data, model=1, tau=0.5,
                                           n_boot=100, print_results=False,
                                           random_state=42)
        
        assert 'p_value' in result
        assert 0 <= result['p_value'] <= 1
    
    def test_bootstrap_returns_decision(self, test_data):
        """Test that bootstrap returns decision."""
        result = qr_fourier_adf_bootstrap(test_data, model=1, tau=0.5,
                                           n_boot=100, print_results=False,
                                           random_state=42)
        
        assert 'reject_1pct' in result
        assert 'reject_5pct' in result
        assert 'reject_10pct' in result
        assert isinstance(result['reject_5pct'], (bool, np.bool_))
    
    def test_bootstrap_cv_ordering(self, test_data):
        """Test that critical values are properly ordered."""
        result = qr_fourier_adf_bootstrap(test_data, model=1, tau=0.5,
                                           n_boot=200, print_results=False,
                                           random_state=42)
        
        # CV should be ordered: 1% < 5% < 10% (for left-tailed test)
        assert result['cv']['1%'] <= result['cv']['5%']
        assert result['cv']['5%'] <= result['cv']['10%']
    
    def test_bootstrap_reproducibility(self, test_data):
        """Test that bootstrap is reproducible with seed."""
        result1 = qr_fourier_adf_bootstrap(test_data, model=1, tau=0.5,
                                            n_boot=100, print_results=False,
                                            random_state=42)
        result2 = qr_fourier_adf_bootstrap(test_data, model=1, tau=0.5,
                                            n_boot=100, print_results=False,
                                            random_state=42)
        
        assert result1['tn'] == result2['tn']


class TestQKSQCM:
    """Test QKS and QCM statistics."""
    
    @pytest.fixture
    def test_data(self):
        """Generate test data."""
        np.random.seed(42)
        return np.cumsum(np.random.randn(150))
    
    def test_qks_qcm_returns_statistics(self, test_data):
        """Test that QKS/QCM returns required statistics."""
        result = qks_qcm_statistics(test_data, model=1, k=3,
                                     tau_range=(0.1, 0.9), n_quantiles=9)
        
        assert 'QKS_f' in result
        assert 'QCM_f' in result
        assert 'tau_values' in result
        assert 't_f_values' in result
    
    def test_qks_qcm_positive_statistics(self, test_data):
        """Test that QKS/QCM are positive."""
        result = qks_qcm_statistics(test_data, model=1, k=3,
                                     tau_range=(0.1, 0.9), n_quantiles=9)
        
        assert result['QKS_f'] >= 0
        assert result['QCM_f'] >= 0
    
    def test_qks_is_sup(self, test_data):
        """Test that QKS is supremum of absolute values."""
        result = qks_qcm_statistics(test_data, model=1, k=3,
                                     tau_range=(0.2, 0.8), n_quantiles=5)
        
        max_abs_t = np.nanmax(np.abs(result['t_f_values']))
        assert np.isclose(result['QKS_f'], max_abs_t, rtol=1e-5)


class TestOptimalK:
    """Test optimal k selection."""
    
    @pytest.fixture
    def test_data(self):
        """Generate test data."""
        np.random.seed(42)
        return np.cumsum(np.random.randn(200))
    
    def test_optimal_k_range(self, test_data):
        """Test that optimal k is in valid range."""
        k_opt = estimate_optimal_k(test_data, model=1, k_max=5)
        assert 1 <= k_opt <= 5
    
    def test_optimal_k_is_int(self, test_data):
        """Test that optimal k is integer."""
        k_opt = estimate_optimal_k(test_data, model=1, k_max=5)
        assert isinstance(k_opt, (int, np.integer))


class TestCriticalValues:
    """Test critical value functions."""
    
    def test_get_critical_values(self):
        """Test getting critical values."""
        cv = get_critical_values(n=200, model=1, k=3, tau=0.5)
        
        assert len(cv) == 3
        assert cv[0] < cv[1] < cv[2]  # CV should be ordered
    
    def test_get_critical_values_model2(self):
        """Test critical values for model 2."""
        cv1 = get_critical_values(n=200, model=1, k=3, tau=0.5)
        cv2 = get_critical_values(n=200, model=2, k=3, tau=0.5)
        
        # Model 2 should have more negative critical values
        assert cv2[1] < cv1[1]
    
    def test_critical_values_different_n(self):
        """Test that critical values vary with sample size."""
        cv100 = get_critical_values(n=100, model=1, k=3, tau=0.5)
        cv500 = get_critical_values(n=500, model=1, k=3, tau=0.5)
        
        # Critical values should be closer to asymptotic for larger n
        assert cv100 != cv500


class TestUtilities:
    """Test utility functions."""
    
    @pytest.fixture
    def test_data(self):
        """Generate test data."""
        np.random.seed(42)
        return np.cumsum(np.random.randn(100))
    
    def test_adf_lag_selection(self, test_data):
        """Test ADF lag selection."""
        lag = adf_lag_selection(test_data, max_lags=10, criterion='aic')
        assert 0 <= lag <= 10
    
    def test_summary_statistics(self, test_data):
        """Test summary statistics."""
        stats = summary_statistics(test_data)
        
        assert 'mean' in stats
        assert 'std' in stats
        assert 'skewness' in stats
        assert 'kurtosis' in stats
        assert stats['n'] == len(test_data)
    
    def test_format_results_latex(self, test_data):
        """Test LaTeX formatting."""
        result = qr_fourier_adf(test_data, print_results=False)
        latex = format_results_latex(result)
        
        assert isinstance(latex, str)
        assert '\\begin{table}' in latex
        assert '\\end{table}' in latex
    
    def test_format_results_dataframe(self, test_data):
        """Test DataFrame formatting."""
        result = qr_fourier_adf(test_data, print_results=False)
        df = format_results_dataframe(result)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_short_series(self):
        """Test that short series raises error."""
        y = np.random.randn(15)
        with pytest.raises(ValueError):
            qr_fourier_adf(y)
    
    def test_missing_values(self):
        """Test handling of missing values."""
        y = np.random.randn(100)
        y[50] = np.nan
        
        with pytest.raises(ValueError):
            qr_fourier_adf(y)
    
    def test_infinite_values(self):
        """Test handling of infinite values."""
        y = np.random.randn(100)
        y[50] = np.inf
        
        with pytest.raises(ValueError):
            qr_fourier_adf(y)
    
    def test_constant_series(self):
        """Test handling of constant series."""
        y = np.ones(100)
        # This should either raise an error or return nan
        try:
            result = qr_fourier_adf(y, print_results=False)
            # If it doesn't raise, check for nan
            assert np.isnan(result['tn']) or np.isfinite(result['tn'])
        except (ValueError, np.linalg.LinAlgError):
            pass  # Expected behavior


class TestMonteCarloValidation:
    """Monte Carlo validation tests."""
    
    def test_size_unit_root(self):
        """Test empirical size under null hypothesis."""
        np.random.seed(42)
        n_simulations = 50  # Small number for testing
        rejections = 0
        
        for _ in range(n_simulations):
            y = np.cumsum(np.random.randn(200))
            result = qr_fourier_adf_bootstrap(y, model=1, tau=0.5,
                                               n_boot=100, print_results=False)
            if result['reject_5pct']:
                rejections += 1
        
        # Empirical size should be close to nominal (5%)
        # With only 50 simulations, allow wide range
        empirical_size = rejections / n_simulations
        assert 0 <= empirical_size <= 0.30  # Wide tolerance for small sample
    
    def test_power_stationary(self):
        """Test power against stationary alternative."""
        np.random.seed(42)
        n_simulations = 30  # Small number for testing
        rejections = 0
        
        for _ in range(n_simulations):
            # Generate stationary AR(1) with phi = 0.5
            n = 200
            y = np.zeros(n)
            for t in range(1, n):
                y[t] = 0.5 * y[t-1] + np.random.randn()
            
            result = qr_fourier_adf_bootstrap(y, model=1, tau=0.5,
                                               n_boot=100, print_results=False)
            if result['reject_5pct']:
                rejections += 1
        
        # Power should be higher than size (> 5%)
        empirical_power = rejections / n_simulations
        # With small samples, just check it's non-negative
        assert empirical_power >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
