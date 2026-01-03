"""
Unit tests for the FFFFF (Fractional Frequency Flexible Fourier Form) test.

These tests verify the implementation against the methodology described in:
Omay, T. (2015). Economics Letters, 134, 123-126.
"""

import numpy as np
import pytest
from fractionaldouble import FFFFFTest, fffff_test
from fractionaldouble.critical_values import get_fffff_critical_values, get_fffff_f_critical_values


class TestFFFFFBasic:
    """Basic functionality tests for FFFFF test."""
    
    def test_basic_execution(self):
        """Test that the test runs without errors on random data."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = fffff_test(y, model='c')
        
        assert result is not None
        assert isinstance(result.tau_stat, float)
        assert isinstance(result.optimal_k, float)
        assert isinstance(result.f_stat, float)
    
    def test_model_specification(self):
        """Test both model specifications."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result_c = fffff_test(y, model='c')
        result_ct = fffff_test(y, model='c,t')
        
        assert result_c.model == 'c'
        assert result_ct.model == 'c,t'
    
    def test_frequency_bounds(self):
        """Test that optimal frequency is within specified bounds."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = fffff_test(y, k_min=0.5, k_max=1.5, k_increment=0.1)
        
        assert 0.5 <= result.optimal_k <= 1.5
    
    def test_invalid_model(self):
        """Test that invalid model raises error."""
        y = np.random.randn(100)
        
        with pytest.raises(ValueError):
            fffff_test(y, model='invalid')
    
    def test_nan_handling(self):
        """Test that NaN values raise error."""
        y = np.array([1, 2, np.nan, 4, 5])
        
        with pytest.raises(ValueError):
            fffff_test(y)


class TestFFFFFStationary:
    """Tests with stationary data (should reject null)."""
    
    def test_stationary_with_fourier_trend(self):
        """Test on stationary series with Fourier trend - should reject null."""
        np.random.seed(42)
        T = 200
        t = np.arange(1, T + 1)
        
        # Stationary series with Fourier trend
        k_true = 1.3
        trend = 3 * np.sin(2 * np.pi * k_true * t / T) + 2 * np.cos(2 * np.pi * k_true * t / T)
        y = trend + np.random.randn(T) * 0.5
        
        result = fffff_test(y, model='c')
        
        # Optimal k should be close to true k
        assert abs(result.optimal_k - k_true) < 0.5
        # Should reject null (stationary)
        assert result.tau_stat < result.critical_values_tau['10%']


class TestFFFFFNonStationary:
    """Tests with non-stationary data (should not reject null)."""
    
    def test_random_walk(self):
        """Test on pure random walk - should not reject null."""
        np.random.seed(42)
        y = np.random.randn(200).cumsum()
        
        result = fffff_test(y, model='c')
        
        # Should not reject null (has unit root)
        assert result.tau_stat > result.critical_values_tau['5%']


class TestFFFFFCriticalValues:
    """Tests for critical values retrieval."""
    
    def test_critical_values_fractional(self):
        """Test critical values for fractional frequencies."""
        for k in [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]:
            cv = get_fffff_critical_values(k, 200, model='c')
            
            assert '10%' in cv
            assert '5%' in cv
            assert '1%' in cv
            assert cv['1%'] < cv['5%'] < cv['10%']  # Critical values are negative
    
    def test_critical_values_sample_sizes(self):
        """Test critical values interpolation for different sample sizes."""
        cv_100 = get_fffff_critical_values(1.5, 100, model='c')
        cv_500 = get_fffff_critical_values(1.5, 500, model='c')
        cv_300 = get_fffff_critical_values(1.5, 300, model='c')
        
        # Critical values should change with sample size
        # 300 should be between 100 and 500
        assert cv_100['5%'] <= cv_300['5%'] <= cv_500['5%'] or \
               cv_100['5%'] >= cv_300['5%'] >= cv_500['5%']
    
    def test_f_critical_values(self):
        """Test F-test critical values."""
        cv_f = get_fffff_f_critical_values(200, model='c')
        
        assert '10%' in cv_f
        assert '5%' in cv_f
        assert '1%' in cv_f
        assert cv_f['10%'] < cv_f['5%'] < cv_f['1%']  # F values are positive


class TestFFFFFClass:
    """Tests for FFFFFTest class interface."""
    
    def test_class_interface(self):
        """Test using class interface."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        test = FFFFFTest(y, model='c')
        result = test.fit()
        
        assert result is not None
        assert test.results is result
    
    def test_summary_output(self):
        """Test summary string generation."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = fffff_test(y)
        summary = result.summary()
        
        assert "FFFFF" in summary
        assert "Omay (2015)" in summary
        assert "τ^fr_DF" in summary
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result = fffff_test(y)
        d = result.to_dict()
        
        assert 'tau_stat' in d
        assert 'optimal_k' in d
        assert 'f_stat' in d


class TestFFFFFReproducibility:
    """Tests for reproducibility across implementations."""
    
    def test_deterministic_results(self):
        """Test that same data gives same results."""
        np.random.seed(42)
        y = np.random.randn(100).cumsum()
        
        result1 = fffff_test(y, model='c', k_min=0.1, k_max=2.0, k_increment=0.1)
        result2 = fffff_test(y, model='c', k_min=0.1, k_max=2.0, k_increment=0.1)
        
        assert result1.tau_stat == result2.tau_stat
        assert result1.optimal_k == result2.optimal_k


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
