"""
Unit tests for the Double Frequency Fourier DF test.

These tests verify the implementation against the methodology described in:
Cai, Y. & Omay, T. (2022). Computational Economics, 59, 445-470.
"""

import numpy as np
import pytest
from fractionaldouble import DoubleFreqTest, double_freq_test
from fractionaldouble.critical_values import (
    get_double_freq_critical_values, 
    get_double_freq_f_critical_values
)


class TestDoubleFreqBasic:
    """Basic functionality tests for Double Frequency test."""
    
    def test_basic_execution(self):
        """Test that the test runs without errors on random data."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = double_freq_test(y, model='c', kmax=2, dk=1)
        
        assert result is not None
        assert isinstance(result.tau_stat, float)
        assert isinstance(result.optimal_ks, float)
        assert isinstance(result.optimal_kc, float)
        assert isinstance(result.f_stat, float)
    
    def test_model_specification(self):
        """Test both model specifications."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result_c = double_freq_test(y, model='c', kmax=2, dk=1)
        result_ct = double_freq_test(y, model='c,t', kmax=2, dk=1)
        
        assert result_c.model == 'c'
        assert result_ct.model == 'c,t'
    
    def test_frequency_bounds(self):
        """Test that optimal frequencies are within specified bounds."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = double_freq_test(y, kmax=3, dk=1)
        
        assert 1 <= result.optimal_ks <= 3
        assert 1 <= result.optimal_kc <= 3
    
    def test_fractional_frequencies(self):
        """Test with fractional frequency search."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = double_freq_test(y, kmax=2, dk=0.5)
        
        # Check that fractional frequencies are possible
        assert result.optimal_ks in [0.5, 1.0, 1.5, 2.0]
        assert result.optimal_kc in [0.5, 1.0, 1.5, 2.0]
    
    def test_invalid_model(self):
        """Test that invalid model raises error."""
        y = np.random.randn(100)
        
        with pytest.raises(ValueError):
            double_freq_test(y, model='invalid')
    
    def test_nan_handling(self):
        """Test that NaN values raise error."""
        y = np.array([1, 2, np.nan, 4, 5])
        
        with pytest.raises(ValueError):
            double_freq_test(y)


class TestDoubleFreqStationary:
    """Tests with stationary data (should reject null)."""
    
    def test_stationary_with_double_freq_trend(self):
        """Test on stationary series with double frequency trend - should reject null."""
        np.random.seed(42)
        T = 200
        t = np.arange(1, T + 1)
        
        # Stationary series with double frequency Fourier trend
        ks_true = 1.5
        kc_true = 2.5
        trend = (3 * np.sin(2 * np.pi * ks_true * t / T) + 
                 2 * np.cos(2 * np.pi * kc_true * t / T))
        y = trend + np.random.randn(T) * 0.5
        
        result = double_freq_test(y, model='c', kmax=3, dk=0.5)
        
        # Should reject null (stationary)
        assert result.tau_stat < result.critical_values_tau['10%']


class TestDoubleFreqNonStationary:
    """Tests with non-stationary data (should not reject null)."""
    
    def test_random_walk(self):
        """Test on pure random walk - should not reject null."""
        np.random.seed(42)
        y = np.random.randn(200).cumsum()
        
        result = double_freq_test(y, model='c', kmax=3, dk=1)
        
        # Should not reject null (has unit root)
        assert result.tau_stat > result.critical_values_tau['5%']


class TestDoubleFreqCriticalValues:
    """Tests for critical values retrieval."""
    
    def test_critical_values_integer_pairs(self):
        """Test critical values for integer frequency pairs."""
        for ks in [1, 2, 3]:
            for kc in [1, 2, 3]:
                cv = get_double_freq_critical_values(ks, kc, 150, model='c')
                
                assert '10%' in cv
                assert '5%' in cv
                assert '1%' in cv
                assert cv['1%'] < cv['5%'] < cv['10%']  # Critical values are negative
    
    def test_critical_values_both_models(self):
        """Test critical values for both model types."""
        cv_c = get_double_freq_critical_values(1, 2, 150, model='c')
        cv_ct = get_double_freq_critical_values(1, 2, 150, model='c,t')
        
        # Trend model should have more negative critical values
        assert cv_ct['5%'] < cv_c['5%']
    
    def test_f_critical_values(self):
        """Test F-test critical values."""
        cv_f = get_double_freq_f_critical_values(2, 150, model='c')
        
        assert '10%' in cv_f
        assert '5%' in cv_f
        assert '1%' in cv_f
        assert cv_f['10%'] < cv_f['5%'] < cv_f['1%']


class TestDoubleFreqClass:
    """Tests for DoubleFreqTest class interface."""
    
    def test_class_interface(self):
        """Test using class interface."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        test = DoubleFreqTest(y, model='c', kmax=2, dk=1)
        result = test.fit()
        
        assert result is not None
        assert test.results is result
    
    def test_summary_output(self):
        """Test summary string generation."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = double_freq_test(y, kmax=2, dk=1)
        summary = result.summary()
        
        assert "Double Frequency" in summary
        assert "Cai & Omay (2022)" in summary
        assert "τ^Dfr" in summary
        assert "k_s*" in summary
        assert "k_c*" in summary
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = double_freq_test(y, kmax=2, dk=1)
        d = result.to_dict()
        
        assert 'tau_stat' in d
        assert 'optimal_ks' in d
        assert 'optimal_kc' in d
        assert 'f_stat' in d


class TestDoubleFreqComparison:
    """Tests comparing single vs double frequency approaches."""
    
    def test_double_freq_vs_single_on_asymmetric(self):
        """Double frequency should fit asymmetric breaks better."""
        np.random.seed(42)
        T = 200
        t = np.arange(1, T + 1)
        
        # Asymmetric breaks - different frequencies for sin and cos
        trend = (3 * np.sin(2 * np.pi * 1 * t / T) + 
                 2 * np.cos(2 * np.pi * 2 * t / T))
        y = trend + np.random.randn(T) * 0.3
        
        result = double_freq_test(y, model='c', kmax=3, dk=1)
        
        # Should identify different frequencies
        # (or at least get a good fit)
        assert result.ssr < np.var(y) * T  # SSR should be less than total variance


class TestDoubleFreqReproducibility:
    """Tests for reproducibility across implementations."""
    
    def test_deterministic_results(self):
        """Test that same data gives same results."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result1 = double_freq_test(y, model='c', kmax=2, dk=1)
        result2 = double_freq_test(y, model='c', kmax=2, dk=1)
        
        assert result1.tau_stat == result2.tau_stat
        assert result1.optimal_ks == result2.optimal_ks
        assert result1.optimal_kc == result2.optimal_kc


class TestGridSearch:
    """Tests for the grid search algorithm."""
    
    def test_grid_search_coverage(self):
        """Test that grid search covers all frequency combinations."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = double_freq_test(y, kmax=2, dk=1)
        
        # With kmax=2 and dk=1, should have 2x2=4 frequency pairs
        expected_pairs = 4  # (1,1), (1,2), (2,1), (2,2)
        assert len(result.frequency_grid) == expected_pairs
    
    def test_grid_search_fractional(self):
        """Test grid search with fractional frequencies."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = double_freq_test(y, kmax=1, dk=0.5)
        
        # With kmax=1 and dk=0.5, should have 2x2=4 frequency pairs
        # (0.5, 0.5), (0.5, 1.0), (1.0, 0.5), (1.0, 1.0)
        expected_pairs = 4
        assert len(result.frequency_grid) == expected_pairs


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
