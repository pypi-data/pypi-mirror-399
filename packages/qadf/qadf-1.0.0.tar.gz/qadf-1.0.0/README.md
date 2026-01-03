# QADF - Quantile ADF Unit Root Test

[![PyPI version](https://badge.fury.io/py/qadf.svg)](https://badge.fury.io/py/qadf)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python implementation of the **Quantile Autoregression Unit Root Test** proposed by Koenker & Xiao (2004).

## Overview

This package implements the quantile autoregression-based unit root test, which provides:

- **Robust inference** under non-Gaussian disturbances (heavy-tailed distributions)
- **Asymmetric dynamics detection** - the ability to detect different persistence patterns at different quantiles
- **Power gains** over conventional ADF tests with non-normal errors
- **Publication-ready output** and visualization tools

## Reference

```
Koenker, R., Xiao, Z. (2004). Unit Root Quantile Autoregression Inference.
Journal of the American Statistical Association, 99, 775-787.
DOI: 10.1198/016214504000001114
```

## Installation

```bash
pip install qadf
```

Or install from source:

```bash
git clone https://github.com/merwanroudane/quantileadf.git
cd quantileadf
pip install -e .
```

## Quick Start

### Basic Usage

```python
import numpy as np
from qadf import qadf, qadf_process

# Generate a random walk (unit root process)
np.random.seed(42)
y = np.cumsum(np.random.randn(200))

# Test at the median (τ = 0.5)
result = qadf(y, tau=0.5, model='c')
print(result)
```

Output:
```
======================================================================
         Quantile ADF Unit Root Test Results
======================================================================
Reference: Koenker, R., Xiao, Z. (2004). JASA, 99, 775-787.
----------------------------------------------------------------------
Model: Constant
Quantile (τ):           0.500
Number of observations: 197
Number of lags:         1
----------------------------------------------------------------------
                        Estimates
----------------------------------------------------------------------
ρ₁(τ) [QR]:             0.998521
ρ₁ [OLS]:               0.997843
α₀(τ):                  -0.023156
δ²:                     0.182456
Half-life:              ∞
----------------------------------------------------------------------
                     Test Statistics
----------------------------------------------------------------------
tₙ(τ):                  -0.8234
----------------------------------------------------------------------
                     Critical Values
----------------------------------------------------------------------
1% critical value:      -2.9139
5% critical value:      -2.2790
10% critical value:     -1.9172
======================================================================
Note: *** p<0.01, ** p<0.05, * p<0.10
H₀: Unit root (ρ₁ = 1) vs H₁: Stationarity (ρ₁ < 1)
======================================================================
```

### Testing Across Multiple Quantiles

```python
# Test across deciles (0.1, 0.2, ..., 0.9)
result = qadf_process(y, quantiles=np.arange(0.1, 1.0, 0.1))
print(result)

# Export to DataFrame
df = result.to_dataframe()
print(df)
```

### Visualization

```python
from qadf import plot_qadf_process, plot_coefficient_dynamics

# Visualize results
plot_qadf_process(result)
plot_coefficient_dynamics(result, title='Interest Rate Persistence')
```

### Bootstrap Inference

```python
from qadf import bootstrap_pvalue, bootstrap_critical_values

# Get bootstrap p-value
boot_result = bootstrap_pvalue(
    test_statistic=result.results[4].statistic,  # Median result
    y=y,
    tau=0.5,
    model='c',
    p=1,
    n_replications=1000
)

print(f"Bootstrap p-value: {boot_result.pvalue:.4f}")
print(f"Bootstrap 5% CV: {boot_result.critical_values['5%']:.4f}")
```

## Model Specifications

The test supports two model specifications:

| Model | Description | Default |
|-------|-------------|---------|
| `'c'` | Constant only | ✓ (Koenker & Xiao default) |
| `'ct'` | Constant and linear trend | |

## Test Statistics

The package computes:

1. **t-statistic** `tₙ(τ)`: The quantile regression counterpart of the ADF t-ratio
2. **Coefficient statistic** `Uₙ(τ) = n(ρ̂₁(τ) - 1)`: Coefficient-based test
3. **QKS statistics**: Kolmogorov-Smirnov type tests over quantile range
4. **QCM statistics**: Cramér-von Mises type tests over quantile range

## Critical Values

Critical values are based on Hansen (1995), which tabulates critical values for the CADF test. The limiting distribution of the QADF test is:

```
tₙ(τ) → δ(∫₀¹ W̄₁²)^{-1/2} ∫₀¹ W̄₁dW₁ + √(1-δ²)N(0,1)
```

This is a mixture of the Dickey-Fuller distribution and the standard normal, with weights determined by δ (the long-run correlation coefficient).

## API Reference

### Main Functions

| Function | Description |
|----------|-------------|
| `qadf(y, tau, model, pmax, ic)` | Single quantile test |
| `qadf_process(y, quantiles, model, pmax, ic)` | Multiple quantile test |
| `bootstrap_pvalue(...)` | Bootstrap p-value |
| `bootstrap_critical_values(...)` | Bootstrap CVs |
| `get_hansen_critical_values(delta2, model)` | Hansen (1995) CVs |

### Result Objects

- `QADFResult`: Single quantile test results
- `QADFProcessResult`: Multiple quantile test results
- `BootstrapResult`: Bootstrap inference results

## Examples

See the `examples/` directory for:

- `example_basic.py`: Basic usage examples
- `example_interest_rates.py`: Replication of interest rate analysis
- `example_monte_carlo.py`: Monte Carlo simulation studies

## Compatibility

This implementation maintains exact compatibility with:

1. **Original paper methodology**: Koenker & Xiao (2004)
2. **GAUSS code**: By Saban Nazlioglu (TSPDLIB package)
3. **Hansen (1995) critical values**: CADF test tables

## Citation

If you use this package in your research, please cite:

```bibtex
@article{koenker2004unit,
  title={Unit Root Quantile Autoregression Inference},
  author={Koenker, Roger and Xiao, Zhijie},
  journal={Journal of the American Statistical Association},
  volume={99},
  number={467},
  pages={775--787},
  year={2004},
  publisher={Taylor \& Francis},
  doi={10.1198/016214504000001114}
}

@software{qadf2024,
  title={QADF: Quantile ADF Unit Root Test for Python},
  author={Roudane, Merwan},
  year={2024},
  url={https://github.com/merwanroudane/quantileadf}
}
```

## Author

**Dr Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: [https://github.com/merwanroudane](https://github.com/merwanroudane)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Roger Koenker and Zhijie Xiao for the original methodology
- Bruce Hansen for the CADF critical values
- Saban Nazlioglu for the GAUSS implementation reference
