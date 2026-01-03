"""
Fractional Frequency Flexible Fourier Form (FFFFF) Unit Root Test

Implementation based on:
Omay, T. (2015). "Fractional Frequency Flexible Fourier Form to approximate 
smooth breaks in unit root testing." Economics Letters, 134, 123-126.

This module implements the FFFFF-DF type unit root test that uses fractional
frequencies in the Fourier approximation to better capture smooth structural breaks.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Union, Tuple, List
import warnings

from .critical_values import get_fffff_critical_values, get_fffff_f_critical_values
from .utils import (
    generate_fourier_terms, compute_ssr, ols_estimation, 
    optimal_lag_selection, ljung_box_test, adf_regression,
    format_significance, format_significance_f
)


@dataclass
class FFFFFTestResult:
    """
    Results from FFFFF unit root test.
    
    Attributes
    ----------
    tau_stat : float
        The t-statistic for the unit root hypothesis (τ^fr_{DF})
    optimal_k : float
        The optimal (fractional) frequency selected by minimizing SSR
    f_stat : float
        F-statistic for testing the presence of nonlinear trend
    p_lags : int
        Number of augmentation lags used
    model : str
        Model specification ('c' for constant, 'c,t' for constant and trend)
    T : int
        Effective sample size
    ssr : float
        Sum of squared residuals at optimal frequency
    critical_values_tau : dict
        Critical values for τ statistic at 10%, 5%, 1%
    critical_values_f : dict
        Critical values for F statistic at 10%, 5%, 1%
    residuals : np.ndarray
        Residuals from the estimated model
    ljung_box_q : float
        Ljung-Box Q-statistic for serial correlation
    ljung_box_pval : float
        p-value for Ljung-Box test
    conclusion : str
        Test conclusion at 5% significance level
    fourier_coefs : dict
        Estimated Fourier coefficients (sin and cos)
    rho : float
        Estimated coefficient on y_{t-1}
    all_frequencies : np.ndarray
        All frequencies tested in grid search
    all_ssr : np.ndarray
        SSR values for all frequencies
    """
    tau_stat: float
    optimal_k: float
    f_stat: float
    p_lags: int
    model: str
    T: int
    ssr: float
    critical_values_tau: dict
    critical_values_f: dict
    residuals: np.ndarray
    ljung_box_q: float
    ljung_box_pval: float
    conclusion: str
    fourier_coefs: dict
    rho: float
    all_frequencies: np.ndarray
    all_ssr: np.ndarray
    
    def __repr__(self):
        return self.summary()
    
    def summary(self) -> str:
        """Generate formatted summary of test results."""
        sig_tau = format_significance(self.tau_stat, self.critical_values_tau)
        sig_f = format_significance_f(self.f_stat, self.critical_values_f)
        
        lines = [
            "=" * 70,
            "Fractional Frequency Flexible Fourier Form (FFFFF) Unit Root Test",
            "Omay (2015) Economics Letters",
            "=" * 70,
            "",
            f"Model: {'Constant only' if self.model == 'c' else 'Constant and Trend'}",
            f"Sample size (T): {self.T}",
            f"Augmentation lags (p): {self.p_lags}",
            f"Optimal frequency (k^fr): {self.optimal_k:.4f}",
            "",
            "-" * 70,
            "Test Statistics:",
            "-" * 70,
            f"  τ^fr_DF statistic: {self.tau_stat:.4f} {sig_tau}",
            f"  F statistic (nonlinear trend): {self.f_stat:.4f} {sig_f}",
            "",
            "-" * 70,
            "Critical Values (τ^fr_DF):",
            "-" * 70,
            f"  10%: {self.critical_values_tau['10%']:.4f}",
            f"   5%: {self.critical_values_tau['5%']:.4f}",
            f"   1%: {self.critical_values_tau['1%']:.4f}",
            "",
            "-" * 70,
            "Critical Values (F-test for nonlinear trend):",
            "-" * 70,
            f"  10%: {self.critical_values_f['10%']:.4f}",
            f"   5%: {self.critical_values_f['5%']:.4f}",
            f"   1%: {self.critical_values_f['1%']:.4f}",
            "",
            "-" * 70,
            "Model Diagnostics:",
            "-" * 70,
            f"  Sum of Squared Residuals: {self.ssr:.6f}",
            f"  Ljung-Box Q({12}): {self.ljung_box_q:.4f} (p-value: {self.ljung_box_pval:.4f})",
            "",
            "-" * 70,
            "Estimated Coefficients:",
            "-" * 70,
            f"  ρ (coefficient on y_{{t-1}}): {self.rho:.6f}",
            f"  sin(2πk^fr t/T) coefficient: {self.fourier_coefs['sin']:.6f}",
            f"  cos(2πk^fr t/T) coefficient: {self.fourier_coefs['cos']:.6f}",
            "",
            "-" * 70,
            "Conclusion (5% level):",
            "-" * 70,
            f"  {self.conclusion}",
            "",
            "=" * 70,
            "Notes:",
            "  *** significant at 1%, ** significant at 5%, * significant at 10%",
            "  H0: Unit root (series is non-stationary)",
            "  H1: No unit root (series is stationary with Fourier trend)",
            "=" * 70
        ]
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Convert results to dictionary."""
        return {
            'tau_stat': self.tau_stat,
            'optimal_k': self.optimal_k,
            'f_stat': self.f_stat,
            'p_lags': self.p_lags,
            'model': self.model,
            'T': self.T,
            'ssr': self.ssr,
            'critical_values_tau': self.critical_values_tau,
            'critical_values_f': self.critical_values_f,
            'ljung_box_q': self.ljung_box_q,
            'ljung_box_pval': self.ljung_box_pval,
            'conclusion': self.conclusion,
            'fourier_coefs': self.fourier_coefs,
            'rho': self.rho
        }


class FFFFFTest:
    """
    Fractional Frequency Flexible Fourier Form Unit Root Test.
    
    This class implements the FFFFF-DF type unit root test proposed by Omay (2015),
    which extends the Enders and Lee (2012b) Fourier DF test by allowing 
    fractional frequencies.
    
    The test regression is:
    
    Δy_t = ρy_{t-1} + c_1 + c_2*t + c_3*sin(2πk^fr*t/T) + c_4*cos(2πk^fr*t/T) + Σφ_j*Δy_{t-j} + ε_t
    
    where k^fr is a fractional frequency selected to minimize SSR over the 
    interval [k_min, k_max] with specified increment.
    
    Parameters
    ----------
    y : array-like
        Time series data
    model : str, optional
        'c' for constant only, 'c,t' for constant and trend. Default is 'c'.
    max_lag : int, optional
        Maximum lag for augmentation. Default is None (auto-selected).
    lag_criterion : str, optional
        Criterion for lag selection: 'aic', 'bic', 'hqc'. Default is 'aic'.
    k_min : float, optional
        Minimum frequency for grid search. Default is 0.1.
    k_max : float, optional
        Maximum frequency for grid search. Default is 2.0.
    k_increment : float, optional
        Frequency increment for grid search. Default is 0.1.
    
    Attributes
    ----------
    y : np.ndarray
        Input time series
    T : int
        Sample size
    model : str
        Model specification
    results : FFFFFTestResult
        Test results (available after calling fit())
    
    Examples
    --------
    >>> import numpy as np
    >>> from fractionaldouble import FFFFFTest
    >>> 
    >>> # Generate sample data with structural break
    >>> np.random.seed(42)
    >>> T = 200
    >>> t = np.arange(1, T + 1)
    >>> trend = 0.5 * np.sin(2 * np.pi * 1.3 * t / T)  # Fourier trend with k=1.3
    >>> y = trend + np.cumsum(np.random.randn(T) * 0.1)
    >>> 
    >>> # Perform FFFFF test
    >>> test = FFFFFTest(y, model='c')
    >>> results = test.fit()
    >>> print(results)
    
    References
    ----------
    Omay, T. (2015). Fractional Frequency Flexible Fourier Form to approximate 
    smooth breaks in unit root testing. Economics Letters, 134, 123-126.
    
    Enders, W., & Lee, J. (2012b). The flexible Fourier form and Dickey-Fuller 
    type unit root tests. Economics Letters, 117(1), 196-199.
    """
    
    def __init__(self, y: Union[np.ndarray, pd.Series, List], 
                 model: str = 'c',
                 max_lag: Optional[int] = None,
                 lag_criterion: str = 'aic',
                 k_min: float = 0.1,
                 k_max: float = 2.0,
                 k_increment: float = 0.1):
        
        # Convert input to numpy array
        if isinstance(y, pd.Series):
            self.y = y.values.astype(float)
        elif isinstance(y, list):
            self.y = np.array(y, dtype=float)
        else:
            self.y = np.asarray(y, dtype=float)
        
        # Validate input
        if np.any(np.isnan(self.y)):
            raise ValueError("Input series contains NaN values")
        
        self.T = len(self.y)
        
        if self.T < 30:
            warnings.warn("Sample size is small (T < 30). Results may be unreliable.")
        
        # Model specification
        if model not in ['c', 'c,t']:
            raise ValueError("model must be 'c' (constant) or 'c,t' (constant and trend)")
        self.model = model
        
        # Lag selection
        self.max_lag = max_lag
        self.lag_criterion = lag_criterion
        
        # Frequency grid parameters
        if k_min <= 0:
            raise ValueError("k_min must be positive")
        if k_max <= k_min:
            raise ValueError("k_max must be greater than k_min")
        if k_increment <= 0:
            raise ValueError("k_increment must be positive")
        
        self.k_min = k_min
        self.k_max = k_max
        self.k_increment = k_increment
        
        self.results = None
    
    def _compute_ssr_for_frequency(self, k: float, p: int) -> Tuple[float, dict]:
        """
        Compute SSR for a given frequency and lag structure.
        
        Parameters
        ----------
        k : float
            Frequency value
        p : int
            Number of augmentation lags
        
        Returns
        -------
        tuple
            (SSR, regression results dict)
        """
        # Generate Fourier terms
        sin_terms, cos_terms = generate_fourier_terms(self.T, k)
        
        # Run ADF regression with Fourier terms
        results = adf_regression(
            self.y, 
            p=p, 
            model=self.model,
            fourier_sin=sin_terms,
            fourier_cos=cos_terms
        )
        
        return results['ssr'], results
    
    def _grid_search(self, p: int) -> Tuple[float, float, dict, np.ndarray, np.ndarray]:
        """
        Perform grid search to find optimal frequency.
        
        Following Davies (1987) data-driven method as described in Omay (2015):
        Run regression for frequencies in [k_min, k_max] and select k that minimizes SSR.
        
        Parameters
        ----------
        p : int
            Number of augmentation lags
        
        Returns
        -------
        tuple
            (optimal_k, min_ssr, best_results, all_frequencies, all_ssr)
        """
        # Generate frequency grid
        frequencies = np.arange(self.k_min, self.k_max + self.k_increment/2, self.k_increment)
        frequencies = np.round(frequencies, 4)  # Avoid floating point issues
        
        ssr_values = []
        all_results = []
        
        for k in frequencies:
            ssr, results = self._compute_ssr_for_frequency(k, p)
            ssr_values.append(ssr)
            all_results.append(results)
        
        # Find optimal frequency
        min_idx = np.argmin(ssr_values)
        optimal_k = frequencies[min_idx]
        min_ssr = ssr_values[min_idx]
        best_results = all_results[min_idx]
        
        return optimal_k, min_ssr, best_results, frequencies, np.array(ssr_values)
    
    def _compute_f_statistic(self, p: int, optimal_k: float) -> float:
        """
        Compute F-statistic for testing the presence of nonlinear trend.
        
        The F-test compares:
        - H0: α = β = 0 (no Fourier components)
        - H1: α ≠ 0 or β ≠ 0 (Fourier components present)
        
        Parameters
        ----------
        p : int
            Number of augmentation lags
        optimal_k : float
            Optimal frequency from grid search
        
        Returns
        -------
        float
            F-statistic value
        """
        # SSR from restricted model (no Fourier terms)
        results_restricted = adf_regression(self.y, p=p, model=self.model)
        ssr_restricted = results_restricted['ssr']
        
        # SSR from unrestricted model (with Fourier terms)
        sin_terms, cos_terms = generate_fourier_terms(self.T, optimal_k)
        results_unrestricted = adf_regression(
            self.y, p=p, model=self.model,
            fourier_sin=sin_terms, fourier_cos=cos_terms
        )
        ssr_unrestricted = results_unrestricted['ssr']
        T_eff = results_unrestricted['T']
        
        # Number of restrictions (2 for sin and cos coefficients)
        q = 2
        
        # Number of parameters in unrestricted model
        # y_{t-1}, constant, [trend], sin, cos, [p lags]
        k_params = 1 + 1 + (1 if self.model == 'c,t' else 0) + 2 + p
        
        # F-statistic: Eq. (similar to Enders and Lee 2012)
        F_stat = ((ssr_restricted - ssr_unrestricted) / q) / (ssr_unrestricted / (T_eff - k_params))
        
        return F_stat
    
    def fit(self) -> FFFFFTestResult:
        """
        Perform the FFFFF unit root test.
        
        Returns
        -------
        FFFFFTestResult
            Object containing test results
        """
        # Determine optimal lag
        if self.max_lag is None:
            # Rule of thumb: int(12 * (T/100)^0.25)
            self.max_lag = int(12 * (self.T / 100) ** 0.25)
        
        p = optimal_lag_selection(self.y, max_lag=self.max_lag, criterion=self.lag_criterion)
        
        # Grid search for optimal frequency
        optimal_k, min_ssr, best_results, all_freqs, all_ssr = self._grid_search(p)
        
        # Extract test statistic
        tau_stat = best_results['tau_stat']
        rho = best_results['rho']
        T_eff = best_results['T']
        
        # F-statistic for nonlinear trend
        f_stat = self._compute_f_statistic(p, optimal_k)
        
        # Get critical values
        try:
            cv_tau = get_fffff_critical_values(optimal_k, T_eff, self.model)
        except ValueError:
            # If exact critical values not available, use closest
            if optimal_k < 1.1:
                cv_tau = get_fffff_critical_values(1, T_eff, self.model)
            else:
                k_rounded = round(optimal_k, 1)
                k_rounded = max(1.1, min(1.9, k_rounded))
                cv_tau = get_fffff_critical_values(k_rounded, T_eff, self.model)
        
        cv_f = get_fffff_f_critical_values(T_eff, self.model)
        
        # Ljung-Box test for serial correlation
        lb_q, lb_pval = ljung_box_test(best_results['residuals'], lags=12, df_adjust=p)
        
        # Extract Fourier coefficients
        # Coefficient order: y_{t-1}, constant, [trend], sin, cos, [lags]
        sin_idx = 2 if self.model == 'c' else 3
        cos_idx = sin_idx + 1
        fourier_coefs = {
            'sin': best_results['coefficients'][sin_idx],
            'cos': best_results['coefficients'][cos_idx]
        }
        
        # Determine conclusion
        if tau_stat < cv_tau['5%']:
            conclusion = "Reject H0 at 5% level: Series is stationary with Fourier trend"
        else:
            conclusion = "Cannot reject H0 at 5% level: Series has a unit root"
        
        # Store and return results
        self.results = FFFFFTestResult(
            tau_stat=tau_stat,
            optimal_k=optimal_k,
            f_stat=f_stat,
            p_lags=p,
            model=self.model,
            T=T_eff,
            ssr=min_ssr,
            critical_values_tau=cv_tau,
            critical_values_f=cv_f,
            residuals=best_results['residuals'],
            ljung_box_q=lb_q,
            ljung_box_pval=lb_pval,
            conclusion=conclusion,
            fourier_coefs=fourier_coefs,
            rho=rho,
            all_frequencies=all_freqs,
            all_ssr=all_ssr
        )
        
        return self.results
    
    def plot_frequency_selection(self, ax=None):
        """
        Plot SSR across frequencies to visualize frequency selection.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates new figure.
        
        Returns
        -------
        matplotlib.axes.Axes
            The axes with the plot
        """
        if self.results is None:
            raise ValueError("Must call fit() before plotting")
        
        import matplotlib.pyplot as plt
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(self.results.all_frequencies, self.results.all_ssr, 'b-', linewidth=2)
        ax.axvline(self.results.optimal_k, color='r', linestyle='--', 
                   label=f'Optimal k = {self.results.optimal_k:.2f}')
        ax.scatter([self.results.optimal_k], [self.results.ssr], color='r', s=100, zorder=5)
        
        ax.set_xlabel('Frequency (k)', fontsize=12)
        ax.set_ylabel('Sum of Squared Residuals (SSR)', fontsize=12)
        ax.set_title('FFFFF Test: Frequency Selection via SSR Minimization', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_fourier_fit(self, ax=None):
        """
        Plot the series with fitted Fourier trend.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates new figure.
        
        Returns
        -------
        matplotlib.axes.Axes
            The axes with the plot
        """
        if self.results is None:
            raise ValueError("Must call fit() before plotting")
        
        import matplotlib.pyplot as plt
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        
        # Compute Fourier trend
        t = np.arange(1, self.T + 1)
        sin_t = np.sin(2 * np.pi * self.results.optimal_k * t / self.T)
        cos_t = np.cos(2 * np.pi * self.results.optimal_k * t / self.T)
        
        fourier_trend = (self.results.fourier_coefs['sin'] * sin_t + 
                        self.results.fourier_coefs['cos'] * cos_t)
        
        ax.plot(t, self.y, 'b-', linewidth=1, label='Original series', alpha=0.7)
        ax.plot(t, fourier_trend + np.mean(self.y), 'r-', linewidth=2, 
                label=f'Fourier trend (k={self.results.optimal_k:.2f})')
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title('FFFFF Test: Series with Fourier Trend', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax


def fffff_test(y: Union[np.ndarray, pd.Series, List],
               model: str = 'c',
               max_lag: Optional[int] = None,
               lag_criterion: str = 'aic',
               k_min: float = 0.1,
               k_max: float = 2.0,
               k_increment: float = 0.1) -> FFFFFTestResult:
    """
    Convenience function to perform FFFFF unit root test.
    
    Parameters
    ----------
    y : array-like
        Time series data
    model : str, optional
        'c' for constant only, 'c,t' for constant and trend. Default is 'c'.
    max_lag : int, optional
        Maximum lag for augmentation. Default is None (auto-selected).
    lag_criterion : str, optional
        Criterion for lag selection: 'aic', 'bic', 'hqc'. Default is 'aic'.
    k_min : float, optional
        Minimum frequency for grid search. Default is 0.1.
    k_max : float, optional
        Maximum frequency for grid search. Default is 2.0.
    k_increment : float, optional
        Frequency increment for grid search. Default is 0.1.
    
    Returns
    -------
    FFFFFTestResult
        Object containing test results
    
    Examples
    --------
    >>> import numpy as np
    >>> from fractionaldouble import fffff_test
    >>> 
    >>> y = np.random.randn(200).cumsum()  # Random walk
    >>> results = fffff_test(y, model='c')
    >>> print(results.tau_stat, results.optimal_k)
    
    References
    ----------
    Omay, T. (2015). Fractional Frequency Flexible Fourier Form to approximate 
    smooth breaks in unit root testing. Economics Letters, 134, 123-126.
    """
    test = FFFFFTest(
        y=y,
        model=model,
        max_lag=max_lag,
        lag_criterion=lag_criterion,
        k_min=k_min,
        k_max=k_max,
        k_increment=k_increment
    )
    return test.fit()
