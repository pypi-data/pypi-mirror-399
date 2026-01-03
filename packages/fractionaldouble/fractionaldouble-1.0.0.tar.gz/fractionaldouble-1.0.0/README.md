# fractionaldouble

[![PyPI version](https://badge.fury.io/py/fractionaldouble.svg)](https://badge.fury.io/py/fractionaldouble)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Fourier-based Unit Root Tests with Fractional and Double Frequencies**

A Python package implementing advanced unit root tests that use Fourier functions to approximate smooth structural breaks in time series data.

## Overview

This package implements two Fourier-based Dickey-Fuller unit root tests:

### 1. Fractional Frequency Flexible Fourier Form (FFFFF) Test
Based on: **Omay, T. (2015)**. "Fractional Frequency Flexible Fourier Form to approximate smooth breaks in unit root testing." *Economics Letters*, 134, 123-126.

### 2. Double Frequency Fourier Dickey-Fuller (DFDF) Test
Based on: **Cai, Y. & Omay, T. (2022)**. "Using Double Frequency in Fourier Dickey-Fuller Unit Root Test." *Computational Economics*, 59, 445-470.

## Features

- 📊 **Fractional Frequency Selection**: Unlike integer-only approaches, allows fractional frequencies for better fit
- 🔄 **Double Frequency Approach**: Separate frequencies for sine and cosine components to capture asymmetric breaks
- 📈 **Publication-Ready Output**: Formatted results suitable for academic publications
- 🧪 **Comprehensive Testing**: Includes F-tests for nonlinear trend and Ljung-Box diagnostics
- 📉 **Visualization**: Built-in plotting functions for frequency selection and Fourier fits
- ✅ **Critical Values**: Complete critical value tables from the original papers

## Installation

```bash
pip install fractionaldouble
```

Or install from source:

```bash
git clone https://github.com/merwanroudane/fractionaldouble.git
cd fractionaldouble
pip install -e .
```

## Quick Start

### FFFFF Test (Omay, 2015)

```python
import numpy as np
from fractionaldouble import fffff_test

# Generate sample data
np.random.seed(42)
T = 200
t = np.arange(1, T + 1)
trend = 3 * np.sin(2 * np.pi * 1.3 * t / T)  # Fourier trend with k=1.3
y = trend + np.random.randn(T).cumsum() * 0.1

# Perform FFFFF test
results = fffff_test(y, model='c', k_min=0.1, k_max=2.0, k_increment=0.1)
print(results)
```

### Double Frequency Test (Cai & Omay, 2022)

```python
import numpy as np
from fractionaldouble import double_freq_test

# Generate sample data with asymmetric breaks
np.random.seed(42)
T = 200
t = np.arange(1, T + 1)
trend = (3 * np.sin(2 * np.pi * 1.5 * t / T) + 
         2 * np.cos(2 * np.pi * 2.5 * t / T))
y = trend + np.random.randn(T).cumsum() * 0.1

# Perform Double Frequency test with integer frequencies
results_int = double_freq_test(y, model='c', kmax=3, dk=1)
print(results_int)

# Perform Double Frequency test with fractional frequencies
results_frac = double_freq_test(y, model='c', kmax=3, dk=0.1)
print(results_frac)
```

## Detailed Usage

### FFFFF Test Parameters

```python
from fractionaldouble import FFFFFTest

test = FFFFFTest(
    y,                    # Time series data
    model='c',            # 'c' for constant, 'c,t' for constant and trend
    max_lag=None,         # Maximum augmentation lag (auto-selected if None)
    lag_criterion='aic',  # Lag selection criterion: 'aic', 'bic', 'hqc'
    k_min=0.1,           # Minimum frequency for grid search
    k_max=2.0,           # Maximum frequency for grid search
    k_increment=0.1      # Frequency increment for grid search
)
results = test.fit()
```

### Double Frequency Test Parameters

```python
from fractionaldouble import DoubleFreqTest

test = DoubleFreqTest(
    y,                    # Time series data
    model='c',            # 'c' for constant, 'c,t' for constant and trend
    max_lag=None,         # Maximum augmentation lag (auto-selected if None)
    lag_criterion='aic',  # Lag selection criterion: 'aic', 'bic', 'hqc'
    kmax=3.0,            # Maximum frequency for grid search
    dk=1.0               # Frequency increment (use 0.1 for fractional)
)
results = test.fit()
```

### Accessing Results

```python
# FFFFF Test Results
print(f"τ statistic: {results.tau_stat}")
print(f"Optimal frequency: {results.optimal_k}")
print(f"F statistic: {results.f_stat}")
print(f"Critical values: {results.critical_values_tau}")
print(f"Conclusion: {results.conclusion}")

# Double Frequency Test Results
print(f"τ statistic: {results.tau_stat}")
print(f"Optimal k_s (sine): {results.optimal_ks}")
print(f"Optimal k_c (cosine): {results.optimal_kc}")
print(f"F statistic: {results.f_stat}")

# Convert to dictionary
results_dict = results.to_dict()
```

### Visualization

```python
# Plot frequency selection
test.plot_frequency_selection()

# Plot Fourier fit
test.plot_fourier_fit()

# For Double Frequency test, compare with single frequency
test.plot_comparison(single_freq_k=1)
```

## Test Methodology

### FFFFF Test (Omay, 2015)

The testing regression is:

$$\Delta y_t = \rho y_{t-1} + c_1 + c_2 t + c_3 \sin\left(\frac{2\pi k^{fr} t}{T}\right) + c_4 \cos\left(\frac{2\pi k^{fr} t}{T}\right) + \sum_{j=1}^{p} \phi_j \Delta y_{t-j} + \varepsilon_t$$

where $k^{fr}$ is a fractional frequency selected to minimize SSR over the interval $[k_{min}, k_{max}]$.

**Advantages over Enders & Lee (2012b)**:
- Fractional frequencies provide better approximation of smooth breaks
- Reduces type II errors and over-filtration problems
- Approximately 20% power improvement in empirical applications

### Double Frequency Test (Cai & Omay, 2022)

The testing regression is:

$$y_t = \sum_{i=0}^{1} c_i t^i + \alpha \sin\left(\frac{2\pi k_s t}{T}\right) + \beta \cos\left(\frac{2\pi k_c t}{T}\right) + \theta y_{t-1} + \varepsilon_t$$

where $(k_s, k_c)$ are selected independently to minimize SSR.

**Advantages**:
- Captures asymmetrically located structural breaks
- Better fit when breaks occur at beginning and end of sample
- More flexible than single frequency approaches

## Critical Values

Critical values are provided from the original papers:

### FFFFF Test (Omay, 2015)
- Table 1: Critical values for $\tau^{fr}_{DF\_C}$ (constant only)
- Table 2: Critical values for $\tau^{fr}_{DF\_\tau}$ (constant and trend)
- F-test critical values for nonlinear trend detection

### Double Frequency Test (Cai & Omay, 2022)
- Table 1: Critical values for $\tau^{Dfr}$ at various frequency pairs
- Table 2: Critical values for $F^{Dfr}$ test

## Examples

### Example 1: Testing Real GDP for Unit Root

```python
import pandas as pd
from fractionaldouble import fffff_test, double_freq_test

# Load your data
# gdp = pd.read_csv('gdp_data.csv')['gdp'].values

# Simulated GDP-like series
np.random.seed(123)
gdp = np.cumsum(np.random.randn(200) * 0.02 + 0.01)

# FFFFF test
result_fffff = fffff_test(gdp, model='c,t')
print(result_fffff)

# Double frequency test
result_double = double_freq_test(gdp, model='c,t', kmax=3, dk=0.1)
print(result_double)
```

### Example 2: Comparing Integer vs Fractional Frequencies

```python
from fractionaldouble import double_freq_test

# Generate data
np.random.seed(42)
y = np.random.randn(200).cumsum()

# Integer frequencies (as in original Enders & Lee)
result_int = double_freq_test(y, kmax=3, dk=1)
print(f"Integer: k_s={result_int.optimal_ks}, k_c={result_int.optimal_kc}, "
      f"SSR={result_int.ssr:.4f}")

# Fractional frequencies (recommended by Omay 2015)
result_frac = double_freq_test(y, kmax=3, dk=0.1)
print(f"Fractional: k_s={result_frac.optimal_ks}, k_c={result_frac.optimal_kc}, "
      f"SSR={result_frac.ssr:.4f}")
```

## Citation

If you use this package in your research, please cite the original papers:

```bibtex
@article{omay2015fractional,
  title={Fractional frequency flexible Fourier form to approximate smooth breaks in unit root testing},
  author={Omay, Tolga},
  journal={Economics Letters},
  volume={134},
  pages={123--126},
  year={2015},
  publisher={Elsevier}
}

@article{cai2022using,
  title={Using double frequency in Fourier Dickey--Fuller unit root test},
  author={Cai, Yifei and Omay, Tolga},
  journal={Computational Economics},
  volume={59},
  number={2},
  pages={445--470},
  year={2022},
  publisher={Springer}
}
```

## References

- Becker, R., Enders, W., & Lee, J. (2006). A stationarity test in the presence of an unknown number of smooth breaks. *Journal of Time Series Analysis*, 27(3), 381-409.
- Davies, R. B. (1987). Hypothesis testing when a nuisance parameter is present only under the alternative. *Biometrika*, 74(1), 33-43.
- Enders, W., & Lee, J. (2012a). A unit root test using a Fourier series to approximate smooth breaks. *Oxford Bulletin of Economics and Statistics*, 74(4), 574-599.
- Enders, W., & Lee, J. (2012b). The flexible Fourier form and Dickey–Fuller type unit root tests. *Economics Letters*, 117(1), 196-199.

## Author

**Dr Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: [https://github.com/merwanroudane/fractionaldouble](https://github.com/merwanroudane/fractionaldouble)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Changelog

### Version 1.0.0
- Initial release
- Implementation of FFFFF test (Omay, 2015)
- Implementation of Double Frequency test (Cai & Omay, 2022)
- Complete critical value tables from original papers
- Comprehensive documentation and examples
