"""
Utility functions for Fourier-based unit root tests.

This module provides helper functions for:
- Generating Fourier terms (sine and cosine components)
- Computing Sum of Squared Residuals (SSR)
- Optimal lag selection using information criteria
- Ljung-Box test for serial correlation
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, Union, List


def generate_fourier_terms(T: int, k: float, double_freq: bool = False, 
                           ks: float = None, kc: float = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate Fourier sine and cosine terms.
    
    Parameters
    ----------
    T : int
        Sample size (number of observations)
    k : float, optional
        Single frequency for both sine and cosine (used when double_freq=False)
    double_freq : bool, optional
        If True, use separate frequencies for sine and cosine. Default is False.
    ks : float, optional
        Frequency for sine component (required when double_freq=True)
    kc : float, optional
        Frequency for cosine component (required when double_freq=True)
    
    Returns
    -------
    tuple of np.ndarray
        (sin_terms, cos_terms) - Fourier sine and cosine terms
    
    Notes
    -----
    The Fourier terms are computed as:
    - sin_t = sin(2 * pi * k * t / T)
    - cos_t = cos(2 * pi * k * t / T)
    
    where t = 1, 2, ..., T
    
    For double frequency (Cai & Omay, 2022):
    - sin_t = sin(2 * pi * ks * t / T)
    - cos_t = cos(2 * pi * kc * t / T)
    """
    t = np.arange(1, T + 1)
    
    if double_freq:
        if ks is None or kc is None:
            raise ValueError("ks and kc must be provided when double_freq=True")
        sin_terms = np.sin(2 * np.pi * ks * t / T)
        cos_terms = np.cos(2 * np.pi * kc * t / T)
    else:
        sin_terms = np.sin(2 * np.pi * k * t / T)
        cos_terms = np.cos(2 * np.pi * k * t / T)
    
    return sin_terms, cos_terms


def compute_ssr(y: np.ndarray, X: np.ndarray) -> float:
    """
    Compute Sum of Squared Residuals from OLS regression.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (T x 1)
    X : np.ndarray
        Design matrix (T x k)
    
    Returns
    -------
    float
        Sum of squared residuals
    """
    # OLS estimation: beta = (X'X)^(-1) X'y
    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        residuals = y - X @ beta
        ssr = np.sum(residuals ** 2)
    except np.linalg.LinAlgError:
        ssr = np.inf
    
    return ssr


def ols_estimation(y: np.ndarray, X: np.ndarray) -> dict:
    """
    Perform OLS estimation and return comprehensive results.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (T x 1)
    X : np.ndarray
        Design matrix (T x k)
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'beta': OLS coefficients
        - 'residuals': OLS residuals
        - 'ssr': Sum of squared residuals
        - 'se': Standard errors of coefficients
        - 't_stats': t-statistics
        - 'sigma2': Estimated variance of residuals
        - 'r_squared': R-squared
        - 'adj_r_squared': Adjusted R-squared
    """
    n, k = X.shape
    
    # OLS estimation
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    
    # Residuals
    y_hat = X @ beta
    residuals = y - y_hat
    
    # Sum of squared residuals
    ssr = np.sum(residuals ** 2)
    
    # Variance estimate
    sigma2 = ssr / (n - k)
    
    # Standard errors
    var_beta = sigma2 * XtX_inv
    se = np.sqrt(np.diag(var_beta))
    
    # t-statistics
    t_stats = beta / se
    
    # R-squared
    ss_total = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - ssr / ss_total if ss_total > 0 else 0
    adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - k) if n > k else 0
    
    return {
        'beta': beta,
        'residuals': residuals,
        'ssr': ssr,
        'se': se,
        't_stats': t_stats,
        'sigma2': sigma2,
        'r_squared': r_squared,
        'adj_r_squared': adj_r_squared
    }


def optimal_lag_selection(y: np.ndarray, max_lag: int = 12, 
                         criterion: str = 'aic') -> int:
    """
    Select optimal lag length using information criteria.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data
    max_lag : int, optional
        Maximum lag to consider. Default is 12.
    criterion : str, optional
        Information criterion to use: 'aic' (Akaike), 'bic' (Bayesian/Schwarz),
        'hqc' (Hannan-Quinn). Default is 'aic'.
    
    Returns
    -------
    int
        Optimal lag length
    
    Notes
    -----
    The information criteria are computed as:
    - AIC = T * ln(SSR/T) + 2k
    - BIC = T * ln(SSR/T) + k * ln(T)
    - HQC = T * ln(SSR/T) + 2k * ln(ln(T))
    
    where k is the number of parameters and T is the sample size.
    """
    T = len(y)
    dy = np.diff(y)
    
    best_ic = np.inf
    best_lag = 0
    
    for p in range(max_lag + 1):
        if p == 0:
            # No lags
            y_reg = dy
            X = np.ones((len(dy), 1))
        else:
            # Create lagged differences
            y_reg = dy[p:]
            X_list = [np.ones(len(y_reg))]
            for j in range(1, p + 1):
                X_list.append(dy[p - j:-j] if j < len(dy) else dy[p - j:])
            X = np.column_stack(X_list)
        
        n = len(y_reg)
        k = X.shape[1]
        
        if n <= k:
            continue
        
        ssr = compute_ssr(y_reg, X)
        
        if criterion == 'aic':
            ic = n * np.log(ssr / n) + 2 * k
        elif criterion == 'bic':
            ic = n * np.log(ssr / n) + k * np.log(n)
        elif criterion == 'hqc':
            ic = n * np.log(ssr / n) + 2 * k * np.log(np.log(n))
        else:
            raise ValueError(f"Unknown criterion: {criterion}")
        
        if ic < best_ic:
            best_ic = ic
            best_lag = p
    
    return best_lag


def ljung_box_test(residuals: np.ndarray, lags: int = 12, 
                   df_adjust: int = 0) -> Tuple[float, float]:
    """
    Perform Ljung-Box test for serial correlation.
    
    Parameters
    ----------
    residuals : np.ndarray
        Residuals from the model
    lags : int, optional
        Number of lags to test. Default is 12.
    df_adjust : int, optional
        Degrees of freedom adjustment for estimated parameters. Default is 0.
    
    Returns
    -------
    tuple
        (Q-statistic, p-value)
    
    Notes
    -----
    The Ljung-Box Q-statistic is computed as:
    Q = T(T+2) * sum_{k=1}^{h} (r_k^2 / (T-k))
    
    where r_k is the sample autocorrelation at lag k, T is the sample size,
    and h is the number of lags.
    
    Under the null hypothesis of no serial correlation, Q follows a 
    chi-squared distribution with (h - df_adjust) degrees of freedom.
    
    References
    ----------
    Ljung, G. M., & Box, G. E. (1978). On a measure of lack of fit in time 
    series models. Biometrika, 65(2), 297-303.
    """
    T = len(residuals)
    residuals = residuals - np.mean(residuals)
    
    # Compute autocorrelations
    acf_values = []
    for k in range(1, lags + 1):
        if k < T:
            r_k = np.corrcoef(residuals[k:], residuals[:-k])[0, 1]
            acf_values.append(r_k)
        else:
            acf_values.append(0)
    
    # Ljung-Box statistic
    Q = T * (T + 2) * np.sum([(r ** 2) / (T - k - 1) for k, r in enumerate(acf_values)])
    
    # Degrees of freedom
    df = max(lags - df_adjust, 1)
    
    # p-value
    p_value = 1 - stats.chi2.cdf(Q, df)
    
    return Q, p_value


def create_diff_matrix(y: np.ndarray) -> np.ndarray:
    """
    Create first difference of a time series.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data
    
    Returns
    -------
    np.ndarray
        First difference: Δy_t = y_t - y_{t-1}
    """
    return np.diff(y)


def create_lagged_diffs(dy: np.ndarray, p: int) -> np.ndarray:
    """
    Create matrix of lagged differences for ADF-type regressions.
    
    Parameters
    ----------
    dy : np.ndarray
        First differenced series
    p : int
        Number of lags
    
    Returns
    -------
    np.ndarray
        Matrix of lagged differences (T-p x p)
    """
    if p == 0:
        return None
    
    T = len(dy)
    lagged_diffs = np.zeros((T - p, p))
    
    for j in range(1, p + 1):
        lagged_diffs[:, j - 1] = dy[p - j:T - j]
    
    return lagged_diffs


def f_test(ssr_restricted: float, ssr_unrestricted: float, 
           q: int, n: int, k: int) -> Tuple[float, float]:
    """
    Perform F-test for nested models.
    
    Parameters
    ----------
    ssr_restricted : float
        Sum of squared residuals from restricted model
    ssr_unrestricted : float
        Sum of squared residuals from unrestricted model
    q : int
        Number of restrictions (difference in parameters)
    n : int
        Sample size
    k : int
        Number of parameters in unrestricted model
    
    Returns
    -------
    tuple
        (F-statistic, p-value)
    """
    F_stat = ((ssr_restricted - ssr_unrestricted) / q) / (ssr_unrestricted / (n - k))
    p_value = 1 - stats.f.cdf(F_stat, q, n - k)
    
    return F_stat, p_value


def adf_regression(y: np.ndarray, p: int = 0, model: str = 'c',
                   fourier_sin: np.ndarray = None, 
                   fourier_cos: np.ndarray = None) -> dict:
    """
    Perform ADF-type regression with optional Fourier terms.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data
    p : int, optional
        Number of lagged differences. Default is 0 (DF test).
    model : str, optional
        'nc' for no constant, 'c' for constant only, 'c,t' for constant and trend.
        Default is 'c'.
    fourier_sin : np.ndarray, optional
        Sine Fourier terms
    fourier_cos : np.ndarray, optional
        Cosine Fourier terms
    
    Returns
    -------
    dict
        Dictionary with regression results including:
        - 'tau_stat': t-statistic for unit root test
        - 'rho': Coefficient on y_{t-1}
        - 'coefficients': All coefficients
        - 'se': Standard errors
        - 'ssr': Sum of squared residuals
        - 'residuals': Residuals
        - 'T': Effective sample size
    """
    T = len(y)
    dy = np.diff(y)
    y_lagged = y[:-1]  # y_{t-1}
    
    # Adjust for lags
    if p > 0:
        # Effective sample
        dy_eff = dy[p:]
        y_lag_eff = y_lagged[p:]
        
        # Lagged differences
        lag_diffs = create_lagged_diffs(dy, p)
        
        # Fourier terms adjustment
        if fourier_sin is not None:
            fourier_sin_eff = fourier_sin[p + 1:]
            fourier_cos_eff = fourier_cos[p + 1:]
        else:
            fourier_sin_eff = None
            fourier_cos_eff = None
    else:
        dy_eff = dy
        y_lag_eff = y_lagged
        lag_diffs = None
        
        if fourier_sin is not None:
            fourier_sin_eff = fourier_sin[1:]
            fourier_cos_eff = fourier_cos[1:]
        else:
            fourier_sin_eff = None
            fourier_cos_eff = None
    
    n_eff = len(dy_eff)
    t_index = np.arange(1, n_eff + 1)
    
    # Build design matrix
    X_list = [y_lag_eff]  # y_{t-1} is first (we need its t-stat)
    
    if model in ['c', 'c,t']:
        X_list.append(np.ones(n_eff))  # Constant
    
    if model == 'c,t':
        X_list.append(t_index)  # Trend
    
    if fourier_sin_eff is not None:
        X_list.append(fourier_sin_eff)
        X_list.append(fourier_cos_eff)
    
    if lag_diffs is not None:
        for j in range(p):
            X_list.append(lag_diffs[:, j])
    
    X = np.column_stack(X_list)
    
    # OLS estimation
    results = ols_estimation(dy_eff, X)
    
    # Extract unit root test statistic (coefficient on y_{t-1})
    rho = results['beta'][0]
    tau_stat = results['t_stats'][0]
    
    return {
        'tau_stat': tau_stat,
        'rho': rho,
        'coefficients': results['beta'],
        'se': results['se'],
        'ssr': results['ssr'],
        'residuals': results['residuals'],
        'T': n_eff,
        'sigma2': results['sigma2'],
        'r_squared': results['r_squared']
    }


def format_significance(value: float, critical_values: dict) -> str:
    """
    Format significance stars based on critical values.
    
    Parameters
    ----------
    value : float
        Test statistic value
    critical_values : dict
        Dictionary with critical values at different significance levels
    
    Returns
    -------
    str
        Significance indicator ('***' for 1%, '**' for 5%, '*' for 10%, '' otherwise)
    """
    if value < critical_values['1%']:
        return '***'
    elif value < critical_values['5%']:
        return '**'
    elif value < critical_values['10%']:
        return '*'
    else:
        return ''


def format_significance_f(value: float, critical_values: dict) -> str:
    """
    Format significance stars for F-test (upper-tail test).
    
    Parameters
    ----------
    value : float
        F-statistic value
    critical_values : dict
        Dictionary with critical values at different significance levels
    
    Returns
    -------
    str
        Significance indicator
    """
    if value > critical_values['1%']:
        return '***'
    elif value > critical_values['5%']:
        return '**'
    elif value > critical_values['10%']:
        return '*'
    else:
        return ''
