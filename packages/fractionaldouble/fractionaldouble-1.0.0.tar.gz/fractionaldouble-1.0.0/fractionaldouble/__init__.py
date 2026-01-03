"""
fractionaldouble: Fourier-based Unit Root Tests with Fractional and Double Frequencies

This package implements two Fourier-based Dickey-Fuller unit root tests:

1. Fractional Frequency Flexible Fourier Form (FFFFF) Test
   Based on: Omay, T. (2015). "Fractional Frequency Flexible Fourier Form to 
   approximate smooth breaks in unit root testing." Economics Letters, 134, 123-126.

2. Double Frequency Fourier Dickey-Fuller (DFDF) Test
   Based on: Cai, Y. & Omay, T. (2022). "Using Double Frequency in Fourier 
   Dickey-Fuller Unit Root Test." Computational Economics, 59, 445-470.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/fractionaldouble
"""

__version__ = "1.0.0"
__author__ = "Dr Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .fffff_test import FFFFFTest, fffff_test
from .double_freq_test import DoubleFreqTest, double_freq_test
from .critical_values import (
    get_fffff_critical_values,
    get_double_freq_critical_values,
    get_fffff_f_critical_values,
    get_double_freq_f_critical_values
)
from .utils import (
    generate_fourier_terms,
    compute_ssr,
    optimal_lag_selection,
    ljung_box_test
)

__all__ = [
    # Main test classes
    'FFFFFTest',
    'DoubleFreqTest',
    # Convenience functions
    'fffff_test',
    'double_freq_test',
    # Critical values
    'get_fffff_critical_values',
    'get_double_freq_critical_values',
    'get_fffff_f_critical_values',
    'get_double_freq_f_critical_values',
    # Utilities
    'generate_fourier_terms',
    'compute_ssr',
    'optimal_lag_selection',
    'ljung_box_test'
]
