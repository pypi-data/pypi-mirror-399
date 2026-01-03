"""
Bootstrap and Resampling Procedures for QADF Test
=================================================

This module implements the bootstrap procedures described in Section 3.2
of Koenker & Xiao (2004) for generating critical values and conducting
inference for the quantile ADF test.

Reference:
    Koenker, R., Xiao, Z., 2004.
    Unit Root Quantile Autoregression Inference.
    Journal of the American Statistical Association 99, 775-787.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantileadf
"""

import numpy as np
from typing import Optional, Tuple, Dict, Union
from dataclasses import dataclass
import warnings
from concurrent.futures import ProcessPoolExecutor
from functools import partial


@dataclass
class BootstrapResult:
    """
    Container for bootstrap results.
    
    Attributes
    ----------
    critical_values : Dict[str, float]
        Bootstrap critical values at various significance levels.
    pvalue : float
        Bootstrap p-value.
    n_replications : int
        Number of bootstrap replications used.
    test_statistic : float
        Original test statistic.
    bootstrap_distribution : np.ndarray
        Array of bootstrap test statistics.
    """
    critical_values: Dict[str, float]
    pvalue: float
    n_replications: int
    test_statistic: float
    bootstrap_distribution: np.ndarray


def _fit_ar(y: np.ndarray, p: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit AR(p) model by OLS.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data.
    p : int
        AR order.
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        AR coefficients and residuals.
    """
    n = len(y)
    
    if p == 0:
        return np.array([]), y - np.mean(y)
    
    # Build design matrix
    Y = y[p:]
    X = np.column_stack([y[p-i-1:n-i-1] for i in range(p)])
    
    # OLS estimation
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    resid = Y - X @ beta
    
    return beta, resid


def generate_bootstrap_sample(y: np.ndarray, p: int, 
                               random_state: Optional[int] = None) -> np.ndarray:
    """
    Generate bootstrap sample following the resampling procedure
    described in Section 3.2 of Koenker & Xiao (2004).
    
    The procedure:
    1. Fit AR(p) to Δy_t and obtain residuals û_t
    2. Draw iid samples {u*_t} from centered residuals
    3. Generate w*_t = Σ β̂_j w*_{t-j} + u*_t
    4. Generate y*_t = y*_{t-1} + w*_t (unit root imposed)
    
    Parameters
    ----------
    y : np.ndarray
        Original time series.
    p : int
        AR order for the first differences.
    random_state : int, optional
        Random seed for reproducibility.
    
    Returns
    -------
    np.ndarray
        Bootstrap sample generated under the unit root null.
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    n = len(y)
    dy = np.diff(y)
    
    # Step 1: Fit AR(p) to first differences
    q = max(p, 1)
    betas, resid = _fit_ar(dy, q)
    
    # Step 2: Center residuals and draw bootstrap sample
    centered_resid = resid - np.mean(resid)
    u_star = np.random.choice(centered_resid, size=len(centered_resid), replace=True)
    
    # Step 3: Generate bootstrap differences
    dy_star = list(dy[:q])  # Initialize with original values
    
    for i in range(len(u_star)):
        if len(betas) > 0:
            dy_star_t = np.sum(betas * np.array(dy_star[-q:])) + u_star[i]
        else:
            dy_star_t = u_star[i]
        dy_star.append(dy_star_t)
    
    # Step 4: Generate bootstrap levels under unit root null
    y_star = [y[0]]
    for i in range(len(dy_star)):
        y_star_t = y_star[i] + dy_star[i]
        y_star.append(y_star_t)
    
    return np.array(y_star[:n])


def _single_bootstrap_statistic(args):
    """
    Helper function to compute a single bootstrap statistic.
    Used for parallel processing.
    """
    y, p, tau, model, rep = args
    from .core import qadf  # Import here to avoid circular imports
    
    y_star = generate_bootstrap_sample(y, p, random_state=rep)
    result = qadf(y_star, tau=tau, model=model, pmax=p, ic='aic', verbose=False)
    
    return result.statistic, result.coefficient_statistic


def bootstrap_critical_values(y: np.ndarray,
                               tau: float,
                               model: str = 'c',
                               p: int = 0,
                               n_replications: int = 1000,
                               random_state: Optional[int] = None,
                               n_jobs: int = 1) -> Dict[str, float]:
    """
    Generate bootstrap critical values for the QADF test.
    
    Parameters
    ----------
    y : np.ndarray
        Original time series.
    tau : float
        Quantile level.
    model : str
        Model type ('c' or 'ct').
    p : int
        Number of lags.
    n_replications : int
        Number of bootstrap replications.
    random_state : int, optional
        Random seed.
    n_jobs : int
        Number of parallel jobs (-1 for all CPUs).
    
    Returns
    -------
    Dict[str, float]
        Dictionary of critical values at 1%, 5%, 10% levels.
    """
    from .core import qadf
    
    if random_state is not None:
        np.random.seed(random_state)
    
    t_stats = []
    u_stats = []
    
    for rep in range(n_replications):
        try:
            y_star = generate_bootstrap_sample(y, p, random_state=rep + (random_state or 0))
            result = qadf(y_star, tau=tau, model=model, pmax=max(p, 1), ic='aic', verbose=False)
            t_stats.append(result.statistic)
            u_stats.append(result.coefficient_statistic)
        except Exception as e:
            warnings.warn(f"Bootstrap replication {rep} failed: {e}")
            continue
    
    t_stats = np.array(t_stats)
    u_stats = np.array(u_stats)
    
    # Calculate critical values (left-tail for unit root test)
    cv_t = {
        '1%': float(np.percentile(t_stats, 1)),
        '2.5%': float(np.percentile(t_stats, 2.5)),
        '5%': float(np.percentile(t_stats, 5)),
        '10%': float(np.percentile(t_stats, 10)),
        '90%': float(np.percentile(t_stats, 90)),
        '95%': float(np.percentile(t_stats, 95)),
        '97.5%': float(np.percentile(t_stats, 97.5)),
        '99%': float(np.percentile(t_stats, 99))
    }
    
    cv_u = {
        '1%': float(np.percentile(u_stats, 1)),
        '2.5%': float(np.percentile(u_stats, 2.5)),
        '5%': float(np.percentile(u_stats, 5)),
        '10%': float(np.percentile(u_stats, 10)),
        '90%': float(np.percentile(u_stats, 90)),
        '95%': float(np.percentile(u_stats, 95)),
        '97.5%': float(np.percentile(u_stats, 97.5)),
        '99%': float(np.percentile(u_stats, 99))
    }
    
    return {'t_stat': cv_t, 'coef_stat': cv_u}


def bootstrap_pvalue(test_statistic: float,
                     y: np.ndarray,
                     tau: float,
                     model: str = 'c',
                     p: int = 0,
                     n_replications: int = 1000,
                     random_state: Optional[int] = None,
                     alternative: str = 'less') -> BootstrapResult:
    """
    Compute bootstrap p-value for the QADF test.
    
    Parameters
    ----------
    test_statistic : float
        The original test statistic.
    y : np.ndarray
        Original time series.
    tau : float
        Quantile level.
    model : str
        Model type.
    p : int
        Number of lags.
    n_replications : int
        Number of bootstrap replications.
    random_state : int, optional
        Random seed.
    alternative : str
        Alternative hypothesis: 'less' (default), 'greater', or 'two-sided'.
    
    Returns
    -------
    BootstrapResult
        Bootstrap inference results.
    """
    from .core import qadf
    
    if random_state is not None:
        np.random.seed(random_state)
    
    boot_stats = []
    
    for rep in range(n_replications):
        try:
            y_star = generate_bootstrap_sample(y, p, random_state=rep + (random_state or 0))
            result = qadf(y_star, tau=tau, model=model, pmax=max(p, 1), ic='aic', verbose=False)
            boot_stats.append(result.statistic)
        except Exception:
            continue
    
    boot_stats = np.array(boot_stats)
    
    # Calculate p-value based on alternative
    if alternative == 'less':
        pvalue = np.mean(boot_stats <= test_statistic)
    elif alternative == 'greater':
        pvalue = np.mean(boot_stats >= test_statistic)
    else:  # two-sided
        pvalue = 2 * min(np.mean(boot_stats <= test_statistic),
                        np.mean(boot_stats >= test_statistic))
    
    # Critical values
    cv = {
        '1%': float(np.percentile(boot_stats, 1)),
        '5%': float(np.percentile(boot_stats, 5)),
        '10%': float(np.percentile(boot_stats, 10))
    }
    
    return BootstrapResult(
        critical_values=cv,
        pvalue=pvalue,
        n_replications=len(boot_stats),
        test_statistic=test_statistic,
        bootstrap_distribution=boot_stats
    )


def bootstrap_qadf_process(y: np.ndarray,
                           quantiles: np.ndarray,
                           model: str = 'c',
                           p: int = 0,
                           n_replications: int = 500,
                           random_state: Optional[int] = None) -> Dict[str, Dict[str, float]]:
    """
    Bootstrap critical values for QKS and QCM statistics.
    
    This implements step 4' from Section 3.3 of Koenker & Xiao (2004).
    
    Parameters
    ----------
    y : np.ndarray
        Original time series.
    quantiles : np.ndarray
        Array of quantiles.
    model : str
        Model type.
    p : int
        Number of lags.
    n_replications : int
        Number of bootstrap replications.
    random_state : int, optional
        Random seed.
    
    Returns
    -------
    Dict
        Bootstrap critical values for QKS_α, QKS_t, QCM_α, QCM_t.
    """
    from .core import qadf_process
    
    if random_state is not None:
        np.random.seed(random_state)
    
    qks_alpha_boot = []
    qks_t_boot = []
    qcm_alpha_boot = []
    qcm_t_boot = []
    
    for rep in range(n_replications):
        try:
            y_star = generate_bootstrap_sample(y, p, random_state=rep + (random_state or 0))
            result = qadf_process(y_star, quantiles=quantiles, model=model, 
                                 pmax=max(p, 1), ic='aic', verbose=False)
            
            qks_alpha_boot.append(result.qks_alpha)
            qks_t_boot.append(result.qks_t)
            qcm_alpha_boot.append(result.qcm_alpha)
            qcm_t_boot.append(result.qcm_t)
        except Exception as e:
            warnings.warn(f"Bootstrap replication {rep} failed: {e}")
            continue
    
    def get_cv(stats):
        return {
            '1%': float(np.percentile(stats, 99)),  # Upper tail for supremum tests
            '5%': float(np.percentile(stats, 95)),
            '10%': float(np.percentile(stats, 90))
        }
    
    return {
        'qks_alpha': get_cv(qks_alpha_boot),
        'qks_t': get_cv(qks_t_boot),
        'qcm_alpha': get_cv(qcm_alpha_boot),
        'qcm_t': get_cv(qcm_t_boot),
        'qks_alpha_5pct': float(np.percentile(qks_alpha_boot, 95)),
        'qks_t_5pct': float(np.percentile(qks_t_boot, 95)),
        'qcm_alpha_5pct': float(np.percentile(qcm_alpha_boot, 95)),
        'qcm_t_5pct': float(np.percentile(qcm_t_boot, 95))
    }


def simulate_critical_values(model: str = 'c',
                              n_obs: int = 500,
                              n_simulations: int = 10000,
                              delta2_values: Optional[np.ndarray] = None,
                              random_state: Optional[int] = None) -> Dict[float, Dict[str, float]]:
    """
    Simulate critical values for the QADF test.
    
    This generates critical values by Monte Carlo simulation under
    the unit root null hypothesis for various values of δ².
    
    Parameters
    ----------
    model : str
        Model type ('c', 'ct', or 'nc').
    n_obs : int
        Sample size for simulation.
    n_simulations : int
        Number of Monte Carlo replications.
    delta2_values : np.ndarray, optional
        Values of δ² to simulate. Default: [0.1, 0.2, ..., 1.0].
    random_state : int, optional
        Random seed.
    
    Returns
    -------
    Dict
        Critical values indexed by δ².
    """
    from scipy.stats import norm
    
    if random_state is not None:
        np.random.seed(random_state)
    
    if delta2_values is None:
        delta2_values = np.arange(0.1, 1.1, 0.1)
    
    results = {}
    
    for delta2 in delta2_values:
        delta = np.sqrt(delta2)
        t_stats = []
        
        for _ in range(n_simulations):
            # Generate two independent standard Brownian motions
            dW1 = np.random.randn(n_obs) / np.sqrt(n_obs)
            dW2 = np.random.randn(n_obs) / np.sqrt(n_obs)
            
            # Cumulative sums (Brownian motions)
            W1 = np.cumsum(dW1)
            W2 = np.cumsum(dW2)
            
            # Demeaned Brownian motion
            W1_bar = W1 - np.mean(W1)
            
            # Mixture: δ * DF component + √(1-δ²) * N(0,1) component
            if model == 'c':
                # Dickey-Fuller distribution component
                numerator = np.sum(W1_bar * dW1)
                denominator = np.sqrt(np.sum(W1_bar**2))
                df_component = numerator / denominator if denominator > 0 else 0
                
                # Standard normal component
                normal_component = np.random.randn()
                
                # Combined statistic (equation 10 from the paper)
                t_stat = delta * df_component + np.sqrt(1 - delta2) * normal_component
                t_stats.append(t_stat)
            elif model == 'ct':
                # With trend (more complex detrending)
                t = np.arange(1, n_obs + 1)
                trend = t / n_obs
                W1_detrended = W1 - np.mean(W1) - (trend - np.mean(trend)) * \
                              (np.sum((trend - np.mean(trend)) * W1) / np.sum((trend - np.mean(trend))**2))
                
                numerator = np.sum(W1_detrended * dW1)
                denominator = np.sqrt(np.sum(W1_detrended**2))
                df_component = numerator / denominator if denominator > 0 else 0
                
                normal_component = np.random.randn()
                t_stat = delta * df_component + np.sqrt(1 - delta2) * normal_component
                t_stats.append(t_stat)
        
        t_stats = np.array(t_stats)
        
        results[delta2] = {
            '1%': float(np.percentile(t_stats, 1)),
            '5%': float(np.percentile(t_stats, 5)),
            '10%': float(np.percentile(t_stats, 10))
        }
    
    return results


def print_critical_value_table(cv_dict: Dict[float, Dict[str, float]], 
                                model: str = 'c') -> str:
    """
    Format critical values as a publication-ready table.
    
    Parameters
    ----------
    cv_dict : Dict
        Dictionary of critical values from simulate_critical_values().
    model : str
        Model type for header.
    
    Returns
    -------
    str
        Formatted table string.
    """
    model_names = {'c': 'Constant', 'ct': 'Constant + Trend', 'nc': 'No Constant'}
    
    lines = [
        f"\nCritical Values for QADF Test - {model_names.get(model, model)}",
        "=" * 50,
        f"{'δ²':>8} {'1%':>12} {'5%':>12} {'10%':>12}",
        "-" * 50
    ]
    
    for delta2 in sorted(cv_dict.keys()):
        cv = cv_dict[delta2]
        lines.append(f"{delta2:>8.2f} {cv['1%']:>12.4f} {cv['5%']:>12.4f} {cv['10%']:>12.4f}")
    
    lines.extend([
        "=" * 50,
        "Source: Monte Carlo simulation",
        ""
    ])
    
    return '\n'.join(lines)
