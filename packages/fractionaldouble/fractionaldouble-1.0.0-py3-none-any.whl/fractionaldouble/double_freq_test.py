"""
Double Frequency Fourier Dickey-Fuller Unit Root Test

Implementation based on:
Cai, Y. & Omay, T. (2022). "Using Double Frequency in Fourier Dickey-Fuller 
Unit Root Test." Computational Economics, 59, 445-470.

This module implements the Double Frequency Fourier DF unit root test that uses
separate frequencies for sine and cosine components to better capture asymmetrically
located structural breaks.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Union, Tuple, List
import warnings

from .critical_values import get_double_freq_critical_values, get_double_freq_f_critical_values
from .utils import (
    generate_fourier_terms, compute_ssr, ols_estimation,
    optimal_lag_selection, ljung_box_test, adf_regression,
    format_significance, format_significance_f
)


@dataclass
class DoubleFreqTestResult:
    """
    Results from Double Frequency Fourier DF unit root test.
    
    Attributes
    ----------
    tau_stat : float
        The t-statistic for the unit root hypothesis (τ^Dfr)
    optimal_ks : float
        The optimal frequency for sine component
    optimal_kc : float
        The optimal frequency for cosine component
    f_stat : float
        F-statistic for testing the presence of nonlinear trend (F^Dfr)
    p_lags : int
        Number of augmentation lags used
    model : str
        Model specification ('c' for constant, 'c,t' for constant and trend)
    T : int
        Effective sample size
    ssr : float
        Sum of squared residuals at optimal frequencies
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
    frequency_grid : np.ndarray
        All frequency pairs tested in grid search (shape: N x 2)
    ssr_grid : np.ndarray
        SSR values for all frequency pairs
    kmax : float
        Maximum frequency used in grid search
    dk : float
        Frequency increment used in grid search
    """
    tau_stat: float
    optimal_ks: float
    optimal_kc: float
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
    frequency_grid: np.ndarray
    ssr_grid: np.ndarray
    kmax: float
    dk: float
    
    def __repr__(self):
        return self.summary()
    
    def summary(self) -> str:
        """Generate formatted summary of test results."""
        sig_tau = format_significance(self.tau_stat, self.critical_values_tau)
        sig_f = format_significance_f(self.f_stat, self.critical_values_f)
        
        lines = [
            "=" * 70,
            "Double Frequency Fourier Dickey-Fuller Unit Root Test",
            "Cai & Omay (2022) Computational Economics",
            "=" * 70,
            "",
            f"Model: {'Constant only' if self.model == 'c' else 'Constant and Trend'}",
            f"Sample size (T): {self.T}",
            f"Augmentation lags (p): {self.p_lags}",
            f"Maximum frequency (kmax): {self.kmax}",
            f"Frequency increment (Δk): {self.dk}",
            "",
            f"Optimal frequency for sin (k_s*): {self.optimal_ks:.4f}",
            f"Optimal frequency for cos (k_c*): {self.optimal_kc:.4f}",
            "",
            "-" * 70,
            "Test Statistics:",
            "-" * 70,
            f"  τ^Dfr statistic: {self.tau_stat:.4f} {sig_tau}",
            f"  F^Dfr statistic (nonlinear trend): {self.f_stat:.4f} {sig_f}",
            "",
            "-" * 70,
            "Critical Values (τ^Dfr):",
            "-" * 70,
            f"  10%: {self.critical_values_tau['10%']:.4f}",
            f"   5%: {self.critical_values_tau['5%']:.4f}",
            f"   1%: {self.critical_values_tau['1%']:.4f}",
            "",
            "-" * 70,
            "Critical Values (F^Dfr for nonlinear trend):",
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
            f"  α (sin(2πk_s t/T) coefficient): {self.fourier_coefs['sin']:.6f}",
            f"  β (cos(2πk_c t/T) coefficient): {self.fourier_coefs['cos']:.6f}",
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
            "  H1: No unit root (series is stationary with double frequency Fourier trend)",
            "=" * 70
        ]
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Convert results to dictionary."""
        return {
            'tau_stat': self.tau_stat,
            'optimal_ks': self.optimal_ks,
            'optimal_kc': self.optimal_kc,
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
            'rho': self.rho,
            'kmax': self.kmax,
            'dk': self.dk
        }


class DoubleFreqTest:
    """
    Double Frequency Fourier Dickey-Fuller Unit Root Test.
    
    This class implements the Double Frequency Fourier DF unit root test proposed 
    by Cai & Omay (2022), which uses separate frequencies for sine and cosine 
    components to better approximate asymmetrically located structural breaks.
    
    The test regression (Equation 3 in the paper) is:
    
    y_t = Σc_i*t^i + α*sin(2πk_s*t/T) + β*cos(2πk_c*t/T) + θ*y_{t-1} + ε_t
    
    Or in augmented form (Equation 10):
    
    Δy_t = Σc_i*t^i + α*sin(2πk_s*t/T) + β*cos(2πk_c*t/T) + Θ*y_{t-1} + Σρ_j*Δy_{t-j} + ε_t
    
    where (k_s, k_c) are selected to minimize SSR over a 2D grid.
    
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
    kmax : float, optional
        Maximum frequency for grid search. Default is 3.0 (as in paper).
    dk : float, optional
        Frequency increment for grid search. Default is 1.0 (integer frequencies).
        Use 0.1 for fractional frequencies as suggested in Cai & Omay (2022).
    
    Attributes
    ----------
    y : np.ndarray
        Input time series
    T : int
        Sample size
    model : str
        Model specification
    results : DoubleFreqTestResult
        Test results (available after calling fit())
    
    Examples
    --------
    >>> import numpy as np
    >>> from fractionaldouble import DoubleFreqTest
    >>> 
    >>> # Generate sample data with asymmetric breaks
    >>> np.random.seed(42)
    >>> T = 200
    >>> t = np.arange(1, T + 1)
    >>> trend = 0.5 * np.sin(2 * np.pi * 1.5 * t / T) + 0.3 * np.cos(2 * np.pi * 2.5 * t / T)
    >>> y = trend + np.cumsum(np.random.randn(T) * 0.1)
    >>> 
    >>> # Perform Double Frequency test with integer frequencies
    >>> test = DoubleFreqTest(y, model='c', kmax=3, dk=1)
    >>> results = test.fit()
    >>> print(results)
    >>> 
    >>> # Perform Double Frequency test with fractional frequencies
    >>> test_frac = DoubleFreqTest(y, model='c', kmax=3, dk=0.1)
    >>> results_frac = test_frac.fit()
    >>> print(results_frac)
    
    References
    ----------
    Cai, Y., & Omay, T. (2022). Using Double Frequency in Fourier Dickey-Fuller 
    Unit Root Test. Computational Economics, 59, 445-470.
    """
    
    def __init__(self, y: Union[np.ndarray, pd.Series, List],
                 model: str = 'c',
                 max_lag: Optional[int] = None,
                 lag_criterion: str = 'aic',
                 kmax: float = 3.0,
                 dk: float = 1.0):
        
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
        if kmax <= 0:
            raise ValueError("kmax must be positive")
        if dk <= 0:
            raise ValueError("dk must be positive")
        
        self.kmax = kmax
        self.dk = dk
        
        self.results = None
    
    def _compute_ssr_for_frequencies(self, ks: float, kc: float, p: int) -> Tuple[float, dict]:
        """
        Compute SSR for given frequency pair and lag structure.
        
        Parameters
        ----------
        ks : float
            Frequency for sine component
        kc : float
            Frequency for cosine component
        p : int
            Number of augmentation lags
        
        Returns
        -------
        tuple
            (SSR, regression results dict)
        """
        # Generate Fourier terms with double frequency
        sin_terms, cos_terms = generate_fourier_terms(
            self.T, k=None, double_freq=True, ks=ks, kc=kc
        )
        
        # Run ADF regression with Fourier terms
        results = adf_regression(
            self.y,
            p=p,
            model=self.model,
            fourier_sin=sin_terms,
            fourier_cos=cos_terms
        )
        
        return results['ssr'], results
    
    def _grid_search(self, p: int) -> Tuple[float, float, float, dict, np.ndarray, np.ndarray]:
        """
        Perform 2D grid search to find optimal frequency pair.
        
        Following the data-driven method in Cai & Omay (2022), Section 2.3:
        Search over all combinations of (ks, kc) and select the pair that minimizes SSR.
        
        Parameters
        ----------
        p : int
            Number of augmentation lags
        
        Returns
        -------
        tuple
            (optimal_ks, optimal_kc, min_ssr, best_results, frequency_grid, ssr_grid)
        """
        # Generate frequency grid
        frequencies = np.arange(self.dk, self.kmax + self.dk/2, self.dk)
        frequencies = np.round(frequencies, 4)  # Avoid floating point issues
        
        n_freq = len(frequencies)
        
        # Store all frequency pairs and their SSR values
        frequency_pairs = []
        ssr_values = []
        all_results = []
        
        # Grid search as described in Section 2.3 of Cai & Omay (2022)
        for ks in frequencies:
            for kc in frequencies:
                ssr, results = self._compute_ssr_for_frequencies(ks, kc, p)
                frequency_pairs.append((ks, kc))
                ssr_values.append(ssr)
                all_results.append(results)
        
        # Find optimal frequency pair
        min_idx = np.argmin(ssr_values)
        optimal_ks, optimal_kc = frequency_pairs[min_idx]
        min_ssr = ssr_values[min_idx]
        best_results = all_results[min_idx]
        
        # Convert to numpy arrays
        frequency_grid = np.array(frequency_pairs)
        ssr_grid = np.array(ssr_values)
        
        return optimal_ks, optimal_kc, min_ssr, best_results, frequency_grid, ssr_grid
    
    def _compute_f_statistic(self, p: int, optimal_ks: float, optimal_kc: float) -> float:
        """
        Compute F-statistic for testing the presence of nonlinear trend.
        
        Following Equation (6) in Cai & Omay (2022):
        F^Dfr(ks, kc) = (SSR0 - SSR1(ks, kc)) / 2 / (SSR1(ks, kc) / (T - q))
        
        where SSR0 is from restricted model (no Fourier) and SSR1 is from unrestricted.
        
        Parameters
        ----------
        p : int
            Number of augmentation lags
        optimal_ks : float
            Optimal sine frequency
        optimal_kc : float
            Optimal cosine frequency
        
        Returns
        -------
        float
            F-statistic value
        """
        # SSR from restricted model (no Fourier terms)
        results_restricted = adf_regression(self.y, p=p, model=self.model)
        ssr_restricted = results_restricted['ssr']
        
        # SSR from unrestricted model (with Fourier terms)
        sin_terms, cos_terms = generate_fourier_terms(
            self.T, k=None, double_freq=True, ks=optimal_ks, kc=optimal_kc
        )
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
        
        # F-statistic: Equation (6) in Cai & Omay (2022)
        F_stat = ((ssr_restricted - ssr_unrestricted) / q) / (ssr_unrestricted / (T_eff - k_params))
        
        return F_stat
    
    def fit(self) -> DoubleFreqTestResult:
        """
        Perform the Double Frequency Fourier DF unit root test.
        
        Returns
        -------
        DoubleFreqTestResult
            Object containing test results
        """
        # Determine optimal lag
        if self.max_lag is None:
            # Rule of thumb: int(12 * (T/100)^0.25)
            self.max_lag = int(12 * (self.T / 100) ** 0.25)
        
        p = optimal_lag_selection(self.y, max_lag=self.max_lag, criterion=self.lag_criterion)
        
        # Grid search for optimal frequency pair
        optimal_ks, optimal_kc, min_ssr, best_results, freq_grid, ssr_grid = self._grid_search(p)
        
        # Extract test statistic
        tau_stat = best_results['tau_stat']
        rho = best_results['rho']
        T_eff = best_results['T']
        
        # F-statistic for nonlinear trend (max F over all frequency pairs)
        # Following Equation (9): F^Dfr(k_s*, k_c*) = max F^Dfr(ks, kc)
        f_stat = self._compute_f_statistic(p, optimal_ks, optimal_kc)
        
        # Get critical values
        # For τ statistic, use closest available frequency pair
        ks_int = int(round(optimal_ks))
        kc_int = int(round(optimal_kc))
        ks_int = max(1, min(3, ks_int))
        kc_int = max(1, min(3, kc_int))
        
        try:
            cv_tau = get_double_freq_critical_values(ks_int, kc_int, T_eff, self.model)
        except ValueError:
            # If exact critical values not available, use (1,1) as fallback
            cv_tau = get_double_freq_critical_values(1, 1, T_eff, self.model)
            warnings.warn(f"Critical values for (ks={ks_int}, kc={kc_int}) not available. "
                         "Using (1,1) as approximation.")
        
        # For F statistic
        kmax_int = int(self.kmax)
        kmax_int = max(1, min(3, kmax_int))
        try:
            cv_f = get_double_freq_f_critical_values(kmax_int, T_eff, self.model, dk=1)
        except ValueError:
            cv_f = get_double_freq_f_critical_values(1, T_eff, self.model, dk=1)
        
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
            conclusion = "Reject H0 at 5% level: Series is stationary with double frequency Fourier trend"
        else:
            conclusion = "Cannot reject H0 at 5% level: Series has a unit root"
        
        # Store and return results
        self.results = DoubleFreqTestResult(
            tau_stat=tau_stat,
            optimal_ks=optimal_ks,
            optimal_kc=optimal_kc,
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
            frequency_grid=freq_grid,
            ssr_grid=ssr_grid,
            kmax=self.kmax,
            dk=self.dk
        )
        
        return self.results
    
    def plot_frequency_selection(self, ax=None):
        """
        Plot SSR surface across frequency pairs to visualize frequency selection.
        
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
        from mpl_toolkits.mplot3d import Axes3D
        
        # Create 3D surface plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Reshape data for surface plot
        frequencies = np.unique(self.results.frequency_grid[:, 0])
        n_freq = len(frequencies)
        
        ks_grid = self.results.frequency_grid[:, 0].reshape(n_freq, n_freq)
        kc_grid = self.results.frequency_grid[:, 1].reshape(n_freq, n_freq)
        ssr_surface = self.results.ssr_grid.reshape(n_freq, n_freq)
        
        surf = ax.plot_surface(ks_grid, kc_grid, ssr_surface, cmap='viridis', alpha=0.7)
        
        # Mark optimal point
        ax.scatter([self.results.optimal_ks], [self.results.optimal_kc], [self.results.ssr],
                   color='red', s=200, marker='*', label='Optimal')
        
        ax.set_xlabel('k_s (sine frequency)', fontsize=12)
        ax.set_ylabel('k_c (cosine frequency)', fontsize=12)
        ax.set_zlabel('SSR', fontsize=12)
        ax.set_title(f'Double Frequency Test: SSR Surface\n'
                    f'Optimal: k_s*={self.results.optimal_ks:.2f}, k_c*={self.results.optimal_kc:.2f}',
                    fontsize=14)
        
        plt.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        return ax
    
    def plot_fourier_fit(self, ax=None):
        """
        Plot the series with fitted double frequency Fourier trend.
        
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
        sin_t = np.sin(2 * np.pi * self.results.optimal_ks * t / self.T)
        cos_t = np.cos(2 * np.pi * self.results.optimal_kc * t / self.T)
        
        fourier_trend = (self.results.fourier_coefs['sin'] * sin_t +
                        self.results.fourier_coefs['cos'] * cos_t)
        
        ax.plot(t, self.y, 'b-', linewidth=1, label='Original series', alpha=0.7)
        ax.plot(t, fourier_trend + np.mean(self.y), 'r-', linewidth=2,
                label=f'Double freq. Fourier trend (k_s={self.results.optimal_ks:.2f}, '
                      f'k_c={self.results.optimal_kc:.2f})')
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title('Double Frequency Fourier DF Test: Series with Fourier Trend', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_comparison(self, single_freq_k: float = None, ax=None):
        """
        Compare double frequency fit with single frequency fit.
        
        Parameters
        ----------
        single_freq_k : float, optional
            Single frequency to compare with. If None, uses k=1 or k=2.
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
        
        t = np.arange(1, self.T + 1)
        
        # Double frequency trend
        sin_t_double = np.sin(2 * np.pi * self.results.optimal_ks * t / self.T)
        cos_t_double = np.cos(2 * np.pi * self.results.optimal_kc * t / self.T)
        trend_double = (self.results.fourier_coefs['sin'] * sin_t_double +
                       self.results.fourier_coefs['cos'] * cos_t_double)
        
        # Single frequency trend
        if single_freq_k is None:
            single_freq_k = 1.0
        
        sin_t_single = np.sin(2 * np.pi * single_freq_k * t / self.T)
        cos_t_single = np.cos(2 * np.pi * single_freq_k * t / self.T)
        
        # Fit single frequency
        X_single = np.column_stack([np.ones(self.T), sin_t_single, cos_t_single])
        beta_single = np.linalg.lstsq(X_single, self.y, rcond=None)[0]
        trend_single = beta_single[1] * sin_t_single + beta_single[2] * cos_t_single
        
        ax.plot(t, self.y, 'b-', linewidth=1, label='Original series', alpha=0.7)
        ax.plot(t, trend_double + np.mean(self.y), 'r-', linewidth=2,
                label=f'Double freq. (k_s={self.results.optimal_ks:.1f}, k_c={self.results.optimal_kc:.1f})')
        ax.plot(t, trend_single + np.mean(self.y), 'g--', linewidth=2,
                label=f'Single freq. (k={single_freq_k:.1f})')
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title('Comparison: Double vs Single Frequency Fourier Trends', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax


def double_freq_test(y: Union[np.ndarray, pd.Series, List],
                     model: str = 'c',
                     max_lag: Optional[int] = None,
                     lag_criterion: str = 'aic',
                     kmax: float = 3.0,
                     dk: float = 1.0) -> DoubleFreqTestResult:
    """
    Convenience function to perform Double Frequency Fourier DF unit root test.
    
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
    kmax : float, optional
        Maximum frequency for grid search. Default is 3.0.
    dk : float, optional
        Frequency increment for grid search. Default is 1.0.
        Use 0.1 for fractional frequencies.
    
    Returns
    -------
    DoubleFreqTestResult
        Object containing test results
    
    Examples
    --------
    >>> import numpy as np
    >>> from fractionaldouble import double_freq_test
    >>> 
    >>> y = np.random.randn(200).cumsum()  # Random walk
    >>> 
    >>> # Integer frequency search
    >>> results_int = double_freq_test(y, model='c', kmax=3, dk=1)
    >>> print(f"Optimal frequencies: ks={results_int.optimal_ks}, kc={results_int.optimal_kc}")
    >>> 
    >>> # Fractional frequency search
    >>> results_frac = double_freq_test(y, model='c', kmax=3, dk=0.1)
    >>> print(f"Optimal frequencies: ks={results_frac.optimal_ks}, kc={results_frac.optimal_kc}")
    
    References
    ----------
    Cai, Y., & Omay, T. (2022). Using Double Frequency in Fourier Dickey-Fuller 
    Unit Root Test. Computational Economics, 59, 445-470.
    """
    test = DoubleFreqTest(
        y=y,
        model=model,
        max_lag=max_lag,
        lag_criterion=lag_criterion,
        kmax=kmax,
        dk=dk
    )
    return test.fit()
