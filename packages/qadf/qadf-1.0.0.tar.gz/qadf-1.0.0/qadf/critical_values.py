"""
Critical Values for Quantile ADF Test
=====================================

This module provides critical values for the QADF test based on:
1. Hansen (1995) CADF critical values
2. Monte Carlo simulated critical values

Reference:
    Hansen, B. (1995). Rethinking the Univariate Approach to Unit Root Tests:
    How to Use Covariates to Increase Power. Econometric Theory, 11, 1148-1171.

    Koenker, R., Xiao, Z. (2004). Unit Root Quantile Autoregression Inference.
    JASA, 99, 775-787.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantileadf
"""

import numpy as np
from typing import Dict, Optional, Tuple
import pandas as pd


# Hansen (1995) Critical Values - Table II (page 1155)
# These are used in the QADF test as the limiting distribution
# is the same as the CADF test.

# No constant model (model = 0 in GAUSS code)
HANSEN_CV_NC = np.array([
    [-2.4611512, -1.7832090, -1.4189957],  # δ² = 0.1
    [-2.4943410, -1.8184897, -1.4589747],  # δ² = 0.2
    [-2.5152783, -1.8516957, -1.5071775],  # δ² = 0.3
    [-2.5509773, -1.8957720, -1.5323511],  # δ² = 0.4
    [-2.5520784, -1.8949965, -1.5418830],  # δ² = 0.5
    [-2.5490848, -1.8981677, -1.5625462],  # δ² = 0.6
    [-2.5547456, -1.9343180, -1.5889045],  # δ² = 0.7
    [-2.5761273, -1.9387996, -1.6020210],  # δ² = 0.8
    [-2.5511921, -1.9328373, -1.6128210],  # δ² = 0.9
    [-2.5658000, -1.9393000, -1.6156000]   # δ² = 1.0
])

# Constant only model (model = 1 in GAUSS code) - Default in Koenker & Xiao (2004)
HANSEN_CV_C = np.array([
    [-2.7844267, -2.1158290, -1.7525193],  # δ² = 0.1
    [-2.9138762, -2.2790427, -1.9172046],  # δ² = 0.2
    [-3.0628184, -2.3994711, -2.0573070],  # δ² = 0.3
    [-3.1376157, -2.5070473, -2.1680520],  # δ² = 0.4
    [-3.1914660, -2.5841611, -2.2520173],  # δ² = 0.5
    [-3.2437157, -2.6399560, -2.3163270],  # δ² = 0.6
    [-3.2951006, -2.7180169, -2.4085640],  # δ² = 0.7
    [-3.3627161, -2.7536756, -2.4577709],  # δ² = 0.8
    [-3.3896556, -2.8074982, -2.5037759],  # δ² = 0.9
    [-3.4336000, -2.8621000, -2.5671000]   # δ² = 1.0
])

# Constant and trend model (model = 2 in GAUSS code)
HANSEN_CV_CT = np.array([
    [-2.9657928, -2.3081543, -1.9519926],  # δ² = 0.1
    [-3.1929596, -2.5482619, -2.1991651],  # δ² = 0.2
    [-3.3727717, -2.7283918, -2.3806008],  # δ² = 0.3
    [-3.4904849, -2.8669056, -2.5315918],  # δ² = 0.4
    [-3.6003166, -2.9853079, -2.6672416],  # δ² = 0.5
    [-3.6819803, -3.0954760, -2.7815263],  # δ² = 0.6
    [-3.7551759, -3.1783550, -2.8728146],  # δ² = 0.7
    [-3.8348596, -3.2674954, -2.9735550],  # δ² = 0.8
    [-3.8800989, -3.3316415, -3.0364171],  # δ² = 0.9
    [-3.9638000, -3.4126000, -3.1279000]   # δ² = 1.0
])


def get_hansen_critical_values(delta2: float, model: str = 'c') -> Dict[str, float]:
    """
    Get interpolated critical values from Hansen (1995) table.
    
    The critical values are for the CADF test, which has the same limiting
    distribution as the QADF test (see Section 3.1 of Koenker & Xiao, 2004).
    
    Parameters
    ----------
    delta2 : float
        The nuisance parameter δ² (squared long-run correlation).
        Valid range: 0 < δ² ≤ 1.
    model : str
        Model specification:
        - 'nc': No constant
        - 'c': Constant only (default)
        - 'ct': Constant and trend
    
    Returns
    -------
    Dict[str, float]
        Critical values at 1%, 5%, and 10% significance levels.
    
    Examples
    --------
    >>> cv = get_hansen_critical_values(0.5, model='c')
    >>> print(f"5% critical value: {cv['5%']:.4f}")
    5% critical value: -2.5842
    """
    # Select appropriate table
    if model == 'nc':
        cv_table = HANSEN_CV_NC
    elif model == 'c':
        cv_table = HANSEN_CV_C
    elif model == 'ct':
        cv_table = HANSEN_CV_CT
    else:
        raise ValueError(f"Unknown model type: {model}. Use 'nc', 'c', or 'ct'.")
    
    # Bound delta2 to valid range
    delta2 = np.clip(delta2, 0.001, 1.0)
    
    # Interpolation based on delta2
    # Table rows correspond to δ² = 0.1, 0.2, ..., 1.0
    if delta2 < 0.1:
        cv = cv_table[0, :]
    elif delta2 >= 1.0:
        cv = cv_table[9, :]
    else:
        # Linear interpolation
        r210 = delta2 * 10
        r2a = int(np.floor(r210))
        r2b = int(np.ceil(r210))
        
        if r2a == r2b or r2a == 0:
            cv = cv_table[max(r2a - 1, 0), :]
        else:
            wa = r2b - r210
            cv = wa * cv_table[r2a - 1, :] + (1 - wa) * cv_table[r2b - 1, :]
    
    return {
        '1%': float(cv[0]),
        '5%': float(cv[1]),
        '10%': float(cv[2])
    }


def get_critical_values_table(model: str = 'c') -> pd.DataFrame:
    """
    Get the full critical values table for a given model.
    
    Parameters
    ----------
    model : str
        Model specification ('nc', 'c', or 'ct').
    
    Returns
    -------
    pd.DataFrame
        DataFrame with δ² as index and critical values as columns.
    """
    if model == 'nc':
        cv_table = HANSEN_CV_NC
    elif model == 'c':
        cv_table = HANSEN_CV_C
    elif model == 'ct':
        cv_table = HANSEN_CV_CT
    else:
        raise ValueError(f"Unknown model type: {model}")
    
    delta2_values = np.arange(0.1, 1.1, 0.1)
    
    df = pd.DataFrame(
        cv_table,
        index=pd.Index(delta2_values, name='δ²'),
        columns=['1%', '5%', '10%']
    )
    
    return df


def print_critical_values_table(model: str = 'c') -> str:
    """
    Print a formatted critical values table.
    
    Parameters
    ----------
    model : str
        Model specification.
    
    Returns
    -------
    str
        Formatted table string.
    """
    model_names = {
        'nc': 'No Constant',
        'c': 'Constant Only (Default)',
        'ct': 'Constant and Trend'
    }
    
    df = get_critical_values_table(model)
    
    header = f"""
╔══════════════════════════════════════════════════════════════════════╗
║     Critical Values for QADF Test - {model_names.get(model, model):^32} ║
╠══════════════════════════════════════════════════════════════════════╣
║  Source: Hansen, B. (1995). Econometric Theory, 11, 1148-1171       ║
║  See also: Koenker, R., Xiao, Z. (2004). JASA, 99, 775-787          ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    
    table_str = df.to_string(float_format='%.4f')
    
    return header + '\n' + table_str


# Additional critical values from simulation (for reference)
# These can be used when δ² is estimated with high uncertainty

SIMULATED_CV_C = {
    0.1: {'1%': -2.78, '5%': -2.12, '10%': -1.75},
    0.2: {'1%': -2.91, '5%': -2.28, '10%': -1.92},
    0.3: {'1%': -3.06, '5%': -2.40, '10%': -2.06},
    0.4: {'1%': -3.14, '5%': -2.51, '10%': -2.17},
    0.5: {'1%': -3.19, '5%': -2.58, '10%': -2.25},
    0.6: {'1%': -3.24, '5%': -2.64, '10%': -2.32},
    0.7: {'1%': -3.30, '5%': -2.72, '10%': -2.41},
    0.8: {'1%': -3.36, '5%': -2.75, '10%': -2.46},
    0.9: {'1%': -3.39, '5%': -2.81, '10%': -2.50},
    1.0: {'1%': -3.43, '5%': -2.86, '10%': -2.57}
}


def get_asymptotic_critical_values_appendix() -> str:
    """
    Get the Appendix A.1 critical values from Koenker & Xiao (2004).
    
    Returns
    -------
    str
        Formatted table as shown in Appendix A.1.
    """
    return """
══════════════════════════════════════════════════════════════════════════
Appendix A.1: Asymptotic Critical Values of the t-Statistic tₙ(τ)
Given by equation (10) in Koenker & Xiao (2004, p. 778)

tₙ(τ) → δ(∫₀¹ W̄₁²)⁻¹/² ∫₀¹ W̄₁dW₁ + √(1-δ²)N(0,1)

══════════════════════════════════════════════════════════════════════════
    δ²         1%         5%        10%
──────────────────────────────────────────────────────────────────────────
   0.1      -2.78      -2.12      -1.75
   0.2      -2.91      -2.28      -1.92
   0.3      -3.06      -2.40      -2.06
   0.4      -3.14      -2.51      -2.17
   0.5      -3.19      -2.58      -2.25
   0.6      -3.24      -2.64      -2.32
   0.7      -3.30      -2.72      -2.41
   0.8      -3.36      -2.75      -2.46
   0.9      -3.39      -2.81      -2.50
══════════════════════════════════════════════════════════════════════════
Source: Hansen (1995), Table II, p. 1155
══════════════════════════════════════════════════════════════════════════
"""


def interpolate_critical_value(delta2: float, 
                                significance: float = 0.05,
                                model: str = 'c') -> float:
    """
    Get an interpolated critical value for any δ² and significance level.
    
    Uses polynomial interpolation for smoother results.
    
    Parameters
    ----------
    delta2 : float
        The nuisance parameter δ².
    significance : float
        Significance level (0.01, 0.05, or 0.10).
    model : str
        Model type.
    
    Returns
    -------
    float
        Interpolated critical value.
    """
    cv_dict = get_hansen_critical_values(delta2, model)
    
    sig_map = {0.01: '1%', 0.05: '5%', 0.10: '10%', 0.1: '10%'}
    
    if significance in sig_map:
        return cv_dict[sig_map[significance]]
    else:
        # Linear interpolation between significance levels
        if significance < 0.05:
            # Between 1% and 5%
            weight = (0.05 - significance) / 0.04
            return weight * cv_dict['1%'] + (1 - weight) * cv_dict['5%']
        else:
            # Between 5% and 10%
            weight = (0.10 - significance) / 0.05
            return weight * cv_dict['5%'] + (1 - weight) * cv_dict['10%']


class CriticalValueTable:
    """
    Class for managing and accessing critical values.
    
    This class provides convenient access to critical values from
    both Hansen (1995) tables and simulated values.
    
    Examples
    --------
    >>> cv_table = CriticalValueTable(model='c')
    >>> cv = cv_table[0.5]  # Get CVs for δ² = 0.5
    >>> print(cv['5%'])
    """
    
    def __init__(self, model: str = 'c'):
        """
        Initialize critical value table.
        
        Parameters
        ----------
        model : str
            Model specification ('nc', 'c', or 'ct').
        """
        self.model = model
        self._table = get_critical_values_table(model)
    
    def __getitem__(self, delta2: float) -> Dict[str, float]:
        """Get critical values for a given δ²."""
        return get_hansen_critical_values(delta2, self.model)
    
    def __repr__(self) -> str:
        """String representation."""
        return print_critical_values_table(self.model)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame."""
        return self._table.copy()
    
    def to_latex(self) -> str:
        """Convert to LaTeX table format."""
        model_names = {
            'nc': 'No Constant',
            'c': 'Constant Only',
            'ct': 'Constant and Trend'
        }
        
        latex = self._table.to_latex(
            float_format='%.4f',
            caption=f'Critical Values for QADF Test ({model_names.get(self.model, self.model)})',
            label=f'tab:qadf_cv_{self.model}'
        )
        
        return latex
