"""
Critical Values for Fourier-based Unit Root Tests

This module contains the critical values tables from:
1. Omay (2015) - Tables 1 and 2 for FFFFF test
2. Cai & Omay (2022) - Tables 1 and 2 for Double Frequency test

All critical values are obtained from Monte Carlo simulations with 20,000 replications
as reported in the original papers.
"""

import numpy as np
from scipy import interpolate

# =============================================================================
# FFFFF Critical Values from Omay (2015) - Table 1
# Critical values for τ^fr_{DF_C} (intercept only)
# =============================================================================

FFFFF_TAU_C_CRITICAL = {
    # k: {T: {significance: value}}
    1.1: {
        100: {'10%': -3.42, '5%': -3.74, '1%': -4.39},
        200: {'10%': -3.39, '5%': -3.72, '1%': -4.33},
        500: {'10%': -3.38, '5%': -3.70, '1%': -4.27},
        1000: {'10%': -3.38, '5%': -3.68, '1%': -4.26}
    },
    1.2: {
        100: {'10%': -3.33, '5%': -3.67, '1%': -4.31},
        200: {'10%': -3.32, '5%': -3.64, '1%': -4.26},
        500: {'10%': -3.31, '5%': -3.63, '1%': -4.23},
        1000: {'10%': -3.30, '5%': -3.62, '1%': -4.21}
    },
    1.3: {
        100: {'10%': -3.26, '5%': -3.62, '1%': -4.29},
        200: {'10%': -3.25, '5%': -3.58, '1%': -4.20},
        500: {'10%': -3.24, '5%': -3.56, '1%': -4.19},
        1000: {'10%': -3.23, '5%': -3.56, '1%': -4.17}
    },
    1.4: {
        100: {'10%': -3.20, '5%': -3.55, '1%': -4.22},
        200: {'10%': -3.19, '5%': -3.53, '1%': -4.17},
        500: {'10%': -3.17, '5%': -3.51, '1%': -4.12},
        1000: {'10%': -3.17, '5%': -3.51, '1%': -4.09}
    },
    1.5: {
        100: {'10%': -3.13, '5%': -3.48, '1%': -4.14},
        200: {'10%': -3.13, '5%': -3.47, '1%': -4.10},
        500: {'10%': -3.12, '5%': -3.45, '1%': -4.07},
        1000: {'10%': -3.11, '5%': -3.45, '1%': -4.07}
    },
    1.6: {
        100: {'10%': -3.07, '5%': -3.42, '1%': -4.10},
        200: {'10%': -3.06, '5%': -3.40, '1%': -4.06},
        500: {'10%': -3.06, '5%': -3.41, '1%': -4.05},
        1000: {'10%': -3.05, '5%': -3.39, '1%': -4.01}
    },
    1.7: {
        100: {'10%': -3.01, '5%': -3.37, '1%': -4.06},
        200: {'10%': -3.00, '5%': -3.36, '1%': -4.01},
        500: {'10%': -3.01, '5%': -3.35, '1%': -3.99},
        1000: {'10%': -2.99, '5%': -3.34, '1%': -3.98}
    },
    1.8: {
        100: {'10%': -2.97, '5%': -3.34, '1%': -4.00},
        200: {'10%': -2.97, '5%': -3.32, '1%': -3.97},
        500: {'10%': -2.96, '5%': -3.30, '1%': -3.95},
        1000: {'10%': -2.96, '5%': -3.31, '1%': -3.93}
    },
    1.9: {
        100: {'10%': -2.94, '5%': -3.30, '1%': -3.99},
        200: {'10%': -2.93, '5%': -3.29, '1%': -3.96},
        500: {'10%': -2.94, '5%': -3.29, '1%': -3.94},
        1000: {'10%': -2.93, '5%': -3.28, '1%': -3.92}
    }
}

# =============================================================================
# FFFFF Critical Values from Omay (2015) - Table 2
# Critical values for τ^fr_{DF_τ} (intercept and trend)
# =============================================================================

FFFFF_TAU_CT_CRITICAL = {
    1.1: {
        100: {'10%': -4.06, '5%': -4.36, '1%': -4.94},
        200: {'10%': -4.01, '5%': -4.30, '1%': -4.87},
        500: {'10%': -4.01, '5%': -4.29, '1%': -4.82},
        1000: {'10%': -4.00, '5%': -4.28, '1%': -4.80}
    },
    1.2: {
        100: {'10%': -4.05, '5%': -4.35, '1%': -4.94},
        200: {'10%': -4.00, '5%': -4.30, '1%': -4.86},
        500: {'10%': -4.00, '5%': -4.28, '1%': -4.83},
        1000: {'10%': -4.00, '5%': -4.27, '1%': -4.80}
    },
    1.3: {
        100: {'10%': -4.03, '5%': -4.34, '1%': -4.94},
        200: {'10%': -4.01, '5%': -4.29, '1%': -4.85},
        500: {'10%': -4.00, '5%': -4.27, '1%': -4.81},
        1000: {'10%': -3.99, '5%': -4.26, '1%': -4.80}
    },
    1.4: {
        100: {'10%': -4.02, '5%': -4.32, '1%': -4.93},
        200: {'10%': -3.98, '5%': -4.28, '1%': -4.85},
        500: {'10%': -3.96, '5%': -4.25, '1%': -4.78},
        1000: {'10%': -3.96, '5%': -4.24, '1%': -4.78}
    },
    1.5: {
        100: {'10%': -3.97, '5%': -4.28, '1%': -4.91},
        200: {'10%': -3.95, '5%': -4.24, '1%': -4.81},
        500: {'10%': -3.93, '5%': -4.21, '1%': -4.78},
        1000: {'10%': -3.92, '5%': -4.21, '1%': -4.76}
    },
    1.6: {
        100: {'10%': -3.92, '5%': -4.23, '1%': -4.85},
        200: {'10%': -3.90, '5%': -4.20, '1%': -4.79},
        500: {'10%': -3.87, '5%': -4.17, '1%': -4.73},
        1000: {'10%': -3.87, '5%': -4.16, '1%': -4.71}
    },
    1.7: {
        100: {'10%': -3.88, '5%': -4.20, '1%': -4.80},
        200: {'10%': -3.84, '5%': -4.15, '1%': -4.74},
        500: {'10%': -3.83, '5%': -4.14, '1%': -4.70},
        1000: {'10%': -3.81, '5%': -4.11, '1%': -4.67}
    },
    1.8: {
        100: {'10%': -3.81, '5%': -4.14, '1%': -4.77},
        200: {'10%': -3.79, '5%': -4.10, '1%': -4.69},
        500: {'10%': -3.77, '5%': -4.08, '1%': -4.64},
        1000: {'10%': -3.76, '5%': -4.06, '1%': -4.64}
    },
    1.9: {
        100: {'10%': -3.76, '5%': -4.09, '1%': -4.70},
        200: {'10%': -3.73, '5%': -4.05, '1%': -4.64},
        500: {'10%': -3.72, '5%': -4.02, '1%': -4.60},
        1000: {'10%': -3.72, '5%': -4.02, '1%': -4.60}
    }
}

# =============================================================================
# FFFFF F-test Critical Values from Omay (2015) - Tables 1 and 2
# Critical values for F(k̂^fr) = Max F(k^fr)
# =============================================================================

FFFFF_F_C_CRITICAL = {
    # Sample size: {significance: value}
    100: {'10%': 8.78, '5%': 10.29, '1%': 13.48},
    200: {'10%': 8.50, '5%': 9.85, '1%': 12.76},
    500: {'10%': 8.33, '5%': 9.64, '1%': 12.37},
    1000: {'10%': 8.31, '5%': 9.60, '1%': 12.31}
}

FFFFF_F_CT_CRITICAL = {
    100: {'10%': 9.38, '5%': 11.07, '1%': 14.62},
    200: {'10%': 9.11, '5%': 10.62, '1%': 13.79},
    500: {'10%': 8.91, '5%': 10.40, '1%': 13.42},
    1000: {'10%': 8.88, '5%': 10.32, '1%': 13.26}
}

# =============================================================================
# Enders and Lee (2012b) Critical Values for Integer Frequencies
# These are used when k is an integer (for comparison)
# =============================================================================

EL_TAU_C_CRITICAL = {
    # Integer frequency critical values from Enders and Lee (2012b)
    1: {
        100: {'10%': -3.65, '5%': -3.95, '1%': -4.55},
        200: {'10%': -3.60, '5%': -3.91, '1%': -4.49},
        500: {'10%': -3.57, '5%': -3.88, '1%': -4.46},
        1000: {'10%': -3.56, '5%': -3.87, '1%': -4.44}
    },
    2: {
        100: {'10%': -3.00, '5%': -3.35, '1%': -4.08},
        200: {'10%': -2.98, '5%': -3.33, '1%': -4.01},
        500: {'10%': -2.96, '5%': -3.31, '1%': -3.97},
        1000: {'10%': -2.95, '5%': -3.30, '1%': -3.95}
    }
}

EL_TAU_CT_CRITICAL = {
    1: {
        100: {'10%': -4.20, '5%': -4.49, '1%': -5.04},
        200: {'10%': -4.14, '5%': -4.42, '1%': -4.96},
        500: {'10%': -4.11, '5%': -4.39, '1%': -4.92},
        1000: {'10%': -4.10, '5%': -4.38, '1%': -4.91}
    },
    2: {
        100: {'10%': -3.73, '5%': -4.06, '1%': -4.66},
        200: {'10%': -3.69, '5%': -4.01, '1%': -4.60},
        500: {'10%': -3.67, '5%': -3.98, '1%': -4.56},
        1000: {'10%': -3.66, '5%': -3.97, '1%': -4.55}
    }
}

# =============================================================================
# Double Frequency Critical Values from Cai & Omay (2022) - Table 1
# Critical values for τ^Dfr (t-statistic)
# =============================================================================

DOUBLE_FREQ_TAU_CRITICAL = {
    # (ks, kc): {T: {'c': {significance: value}, 'c,t': {significance: value}}}
    (1, 1): {
        50: {'c': {'10%': -3.526, '5%': -3.852, '1%': -4.580}, 
             'c,t': {'10%': -4.100, '5%': -4.452, '1%': -5.062}},
        150: {'c': {'10%': -3.486, '5%': -3.798, '1%': -4.403},
              'c,t': {'10%': -4.026, '5%': -4.320, '1%': -4.956}},
        300: {'c': {'10%': -3.455, '5%': -3.762, '1%': -4.363},
              'c,t': {'10%': -4.023, '5%': -4.302, '1%': -4.870}}
    },
    (1, 2): {
        50: {'c': {'10%': -3.502, '5%': -3.910, '1%': -4.739},
             'c,t': {'10%': -4.038, '5%': -4.432, '1%': -5.200}},
        150: {'c': {'10%': -3.463, '5%': -3.823, '1%': -4.480},
              'c,t': {'10%': -3.959, '5%': -4.300, '1%': -4.939}},
        300: {'c': {'10%': -3.394, '5%': -3.781, '1%': -4.468},
              'c,t': {'10%': -3.945, '5%': -4.264, '1%': -4.894}}
    },
    (1, 3): {
        50: {'c': {'10%': -3.332, '5%': -3.755, '1%': -4.509},
             'c,t': {'10%': -3.862, '5%': -4.257, '1%': -5.031}},
        150: {'c': {'10%': -3.260, '5%': -3.615, '1%': -4.360},
              'c,t': {'10%': -3.839, '5%': -4.199, '1%': -4.842}},
        300: {'c': {'10%': -3.320, '5%': -3.662, '1%': -4.314},
              'c,t': {'10%': -3.803, '5%': -4.147, '1%': -4.775}}
    },
    (2, 1): {
        50: {'c': {'10%': -3.481, '5%': -3.882, '1%': -4.744},
             'c,t': {'10%': -4.230, '5%': -4.580, '1%': -5.332}},
        150: {'c': {'10%': -3.371, '5%': -3.761, '1%': -4.426},
              'c,t': {'10%': -4.117, '5%': -4.438, '1%': -5.046}},
        300: {'c': {'10%': -3.349, '5%': -3.731, '1%': -4.390},
              'c,t': {'10%': -4.102, '5%': -4.393, '1%': -4.966}}
    },
    (2, 2): {
        50: {'c': {'10%': -2.888, '5%': -3.274, '1%': -4.013},
             'c,t': {'10%': -3.728, '5%': -4.076, '1%': -4.778}},
        150: {'c': {'10%': -2.909, '5%': -3.271, '1%': -3.942},
              'c,t': {'10%': -3.659, '5%': -4.001, '1%': -4.696}},
        300: {'c': {'10%': -2.906, '5%': -3.257, '1%': -3.934},
              'c,t': {'10%': -3.677, '5%': -3.990, '1%': -4.582}}
    },
    (2, 3): {
        50: {'c': {'10%': -2.927, '5%': -3.367, '1%': -4.210},
             'c,t': {'10%': -3.770, '5%': -4.207, '1%': -5.056}},
        150: {'c': {'10%': -2.907, '5%': -3.283, '1%': -3.975},
              'c,t': {'10%': -3.721, '5%': -4.053, '1%': -4.784}},
        300: {'c': {'10%': -2.895, '5%': -3.259, '1%': -3.946},
              'c,t': {'10%': -3.691, '5%': -4.037, '1%': -4.694}}
    },
    (3, 1): {
        50: {'c': {'10%': -3.252, '5%': -3.646, '1%': -4.522},
             'c,t': {'10%': -4.030, '5%': -4.407, '1%': -5.133}},
        150: {'c': {'10%': -3.238, '5%': -3.609, '1%': -4.392},
              'c,t': {'10%': -3.922, '5%': -4.251, '1%': -4.889}},
        300: {'c': {'10%': -3.202, '5%': -3.576, '1%': -4.258},
              'c,t': {'10%': -3.928, '5%': -4.250, '1%': -4.871}}
    },
    (3, 2): {
        50: {'c': {'10%': -2.885, '5%': -3.269, '1%': -4.061},
             'c,t': {'10%': -3.754, '5%': -4.170, '1%': -5.000}},
        150: {'c': {'10%': -2.864, '5%': -3.278, '1%': -4.044},
              'c,t': {'10%': -3.699, '5%': -4.046, '1%': -4.717}},
        300: {'c': {'10%': -2.891, '5%': -3.273, '1%': -3.960},
              'c,t': {'10%': -3.665, '5%': -4.016, '1%': -4.620}}
    },
    (3, 3): {
        50: {'c': {'10%': -2.705, '5%': -3.081, '1%': -3.868},
             'c,t': {'10%': -3.434, '5%': -3.808, '1%': -4.631}},
        150: {'c': {'10%': -2.716, '5%': -3.056, '1%': -3.727},
              'c,t': {'10%': -3.420, '5%': -3.759, '1%': -4.395}},
        300: {'c': {'10%': -2.704, '5%': -3.026, '1%': -3.646},
              'c,t': {'10%': -3.448, '5%': -3.783, '1%': -4.354}}
    }
}

# =============================================================================
# Double Frequency F-test Critical Values from Cai & Omay (2022) - Table 2
# Critical values for F^Dfr
# =============================================================================

DOUBLE_FREQ_F_CRITICAL = {
    # (kmax, dk): {T: {'c': {significance: value}, 'c,t': {significance: value}}}
    (1, 1): {
        50: {'c': {'10%': 6.097, '5%': 7.521, '1%': 10.982},
             'c,t': {'10%': 7.355, '5%': 8.921, '1%': 12.813}},
        150: {'c': {'10%': 5.701, '5%': 7.076, '1%': 10.027},
              'c,t': {'10%': 7.087, '5%': 8.546, '1%': 11.435}},
        300: {'c': {'10%': 5.708, '5%': 7.017, '1%': 9.674},
              'c,t': {'10%': 6.762, '5%': 8.217, '1%': 11.298}}
    },
    (2, 1): {
        50: {'c': {'10%': 7.479, '5%': 9.099, '1%': 12.731},
             'c,t': {'10%': 8.974, '5%': 10.729, '1%': 14.910}},
        150: {'c': {'10%': 6.842, '5%': 8.165, '1%': 11.198},
              'c,t': {'10%': 8.423, '5%': 9.942, '1%': 13.139}},
        300: {'c': {'10%': 6.734, '5%': 8.023, '1%': 10.461},
              'c,t': {'10%': 8.139, '5%': 9.524, '1%': 12.289}}
    },
    (3, 1): {
        50: {'c': {'10%': 7.939, '5%': 9.478, '1%': 13.175},
             'c,t': {'10%': 9.785, '5%': 11.450, '1%': 15.195}},
        150: {'c': {'10%': 7.400, '5%': 8.701, '1%': 11.504},
              'c,t': {'10%': 9.100, '5%': 10.554, '1%': 13.346}},
        300: {'c': {'10%': 7.107, '5%': 8.372, '1%': 11.197},
              'c,t': {'10%': 8.798, '5%': 10.095, '1%': 12.869}}
    }
}


def _interpolate_critical_value(cv_dict, T, significance):
    """
    Interpolate critical value for non-tabulated sample sizes.
    
    Parameters
    ----------
    cv_dict : dict
        Dictionary with sample sizes as keys and critical values as values
    T : int
        Sample size
    significance : str
        Significance level ('10%', '5%', '1%')
    
    Returns
    -------
    float
        Interpolated critical value
    """
    sample_sizes = sorted(cv_dict.keys())
    values = [cv_dict[s][significance] for s in sample_sizes]
    
    if T <= sample_sizes[0]:
        return values[0]
    elif T >= sample_sizes[-1]:
        return values[-1]
    else:
        # Linear interpolation
        f = interpolate.interp1d(sample_sizes, values, kind='linear')
        return float(f(T))


def get_fffff_critical_values(k, T, model='c'):
    """
    Get critical values for the FFFFF unit root test (Omay, 2015).
    
    Parameters
    ----------
    k : float
        Frequency value (must be between 1.1 and 1.9 for fractional frequencies,
        or 1 or 2 for integer frequencies from Enders & Lee 2012b)
    T : int
        Sample size
    model : str, optional
        'c' for intercept only, 'c,t' for intercept and trend. Default is 'c'.
    
    Returns
    -------
    dict
        Dictionary with critical values at 10%, 5%, and 1% significance levels
    
    References
    ----------
    Omay, T. (2015). Fractional Frequency Flexible Fourier Form to approximate 
    smooth breaks in unit root testing. Economics Letters, 134, 123-126.
    """
    # Check if it's an integer frequency (use Enders & Lee 2012b values)
    if k == 1 or k == 2:
        if model == 'c':
            cv_dict = EL_TAU_C_CRITICAL.get(int(k))
        else:
            cv_dict = EL_TAU_CT_CRITICAL.get(int(k))
    else:
        # Fractional frequency
        k_rounded = round(k, 1)
        if model == 'c':
            cv_dict = FFFFF_TAU_C_CRITICAL.get(k_rounded)
        else:
            cv_dict = FFFFF_TAU_CT_CRITICAL.get(k_rounded)
    
    if cv_dict is None:
        raise ValueError(f"No critical values available for k={k}. "
                        "Valid fractional frequencies: 1.1-1.9 (increment 0.1)")
    
    result = {}
    for sig in ['10%', '5%', '1%']:
        result[sig] = _interpolate_critical_value(cv_dict, T, sig)
    
    return result


def get_fffff_f_critical_values(T, model='c'):
    """
    Get critical values for the F-test of nonlinear trend in FFFFF test (Omay, 2015).
    
    Parameters
    ----------
    T : int
        Sample size
    model : str, optional
        'c' for intercept only, 'c,t' for intercept and trend. Default is 'c'.
    
    Returns
    -------
    dict
        Dictionary with critical values at 10%, 5%, and 1% significance levels
    """
    if model == 'c':
        cv_dict = FFFFF_F_C_CRITICAL
    else:
        cv_dict = FFFFF_F_CT_CRITICAL
    
    result = {}
    for sig in ['10%', '5%', '1%']:
        result[sig] = _interpolate_critical_value(cv_dict, T, sig)
    
    return result


def get_double_freq_critical_values(ks, kc, T, model='c'):
    """
    Get critical values for the Double Frequency Fourier DF test (Cai & Omay, 2022).
    
    Parameters
    ----------
    ks : int
        Frequency for sine component
    kc : int
        Frequency for cosine component
    T : int
        Sample size
    model : str, optional
        'c' for intercept only, 'c,t' for intercept and trend. Default is 'c'.
    
    Returns
    -------
    dict
        Dictionary with critical values at 10%, 5%, and 1% significance levels
    
    References
    ----------
    Cai, Y., & Omay, T. (2022). Using Double Frequency in Fourier Dickey-Fuller 
    Unit Root Test. Computational Economics, 59, 445-470.
    """
    key = (int(round(ks)), int(round(kc)))
    cv_dict = DOUBLE_FREQ_TAU_CRITICAL.get(key)
    
    if cv_dict is None:
        # Try to find closest available
        available_keys = list(DOUBLE_FREQ_TAU_CRITICAL.keys())
        raise ValueError(f"No critical values available for (ks={ks}, kc={kc}). "
                        f"Available frequency pairs: {available_keys}")
    
    # Select model type
    model_key = 'c' if model == 'c' else 'c,t'
    
    result = {}
    for sig in ['10%', '5%', '1%']:
        # Interpolate for sample size
        sample_sizes = sorted(cv_dict.keys())
        values = [cv_dict[s][model_key][sig] for s in sample_sizes]
        
        if T <= sample_sizes[0]:
            result[sig] = values[0]
        elif T >= sample_sizes[-1]:
            result[sig] = values[-1]
        else:
            f = interpolate.interp1d(sample_sizes, values, kind='linear')
            result[sig] = float(f(T))
    
    return result


def get_double_freq_f_critical_values(kmax, T, model='c', dk=1):
    """
    Get critical values for the F-test of nonlinear trend in Double Frequency test.
    
    Parameters
    ----------
    kmax : int
        Maximum frequency used in grid search
    T : int
        Sample size
    model : str, optional
        'c' for intercept only, 'c,t' for intercept and trend. Default is 'c'.
    dk : int, optional
        Frequency increment (default is 1 for integer frequencies)
    
    Returns
    -------
    dict
        Dictionary with critical values at 10%, 5%, and 1% significance levels
    """
    key = (int(kmax), int(dk))
    cv_dict = DOUBLE_FREQ_F_CRITICAL.get(key)
    
    if cv_dict is None:
        available_keys = list(DOUBLE_FREQ_F_CRITICAL.keys())
        raise ValueError(f"No F-test critical values available for (kmax={kmax}, dk={dk}). "
                        f"Available: {available_keys}")
    
    model_key = 'c' if model == 'c' else 'c,t'
    
    result = {}
    for sig in ['10%', '5%', '1%']:
        sample_sizes = sorted(cv_dict.keys())
        values = [cv_dict[s][model_key][sig] for s in sample_sizes]
        
        if T <= sample_sizes[0]:
            result[sig] = values[0]
        elif T >= sample_sizes[-1]:
            result[sig] = values[-1]
        else:
            f = interpolate.interp1d(sample_sizes, values, kind='linear')
            result[sig] = float(f(T))
    
    return result
