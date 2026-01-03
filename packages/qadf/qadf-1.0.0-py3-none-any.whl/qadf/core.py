"""
Quantile Autoregressive Distributed Lag (QADF) Unit Root Test
=============================================================

Implementation of the Quantile Unit Root Test based on:

Reference:
    Koenker, R., Xiao, Z., 2004.
    Unit Root Quantile Autoregression Inference.
    Journal of the American Statistical Association 99, 775-787.
    DOI: 10.1198/016214504000001114

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantileadf

This implementation provides exact compatibility with the original GAUSS code
by Saban Nazlioglu.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm
from typing import Optional, Union, Tuple, List, Dict, Any
from dataclasses import dataclass, field
import warnings


@dataclass
class QADFResult:
    """
    Container for Quantile ADF test results.
    
    Attributes
    ----------
    statistic : float
        The QADF test statistic (t-ratio for a given quantile).
    pvalue : float or None
        The p-value (if bootstrap was used).
    quantile : float
        The quantile at which the test was performed.
    lags : int
        Number of lags used in the regression.
    rho_tau : float
        Estimated autoregressive coefficient at quantile τ.
    rho_ols : float
        OLS estimated autoregressive coefficient.
    alpha_tau : float
        Estimated intercept at quantile τ.
    delta2 : float
        Nuisance parameter δ² (long-run correlation coefficient squared).
    critical_values : dict
        Critical values at 1%, 5%, and 10% significance levels.
    model : str
        Model specification ('c' for constant, 'ct' for constant and trend).
    n_obs : int
        Number of observations used in the regression.
    half_life : float or str
        Half-life of shocks (∞ if negative or rho >= 1).
    """
    statistic: float
    pvalue: Optional[float]
    quantile: float
    lags: int
    rho_tau: float
    rho_ols: float
    alpha_tau: float
    delta2: float
    critical_values: Dict[str, float]
    model: str
    n_obs: int
    half_life: Union[float, str]
    coefficient_statistic: Optional[float] = None
    
    def __repr__(self) -> str:
        """String representation of test results."""
        stars = ''
        if self.statistic < self.critical_values['1%']:
            stars = '***'
        elif self.statistic < self.critical_values['5%']:
            stars = '**'
        elif self.statistic < self.critical_values['10%']:
            stars = '*'
        
        coef_line = f"Uₙ(τ):                  {self.coefficient_statistic:.4f}\n" if self.coefficient_statistic else ""
        
        return (
            f"\n{'='*70}\n"
            f"         Quantile ADF Unit Root Test Results\n"
            f"{'='*70}\n"
            f"Reference: Koenker, R., Xiao, Z. (2004). JASA, 99, 775-787.\n"
            f"{'-'*70}\n"
            f"Model: {'Constant' if self.model == 'c' else 'Constant and Trend'}\n"
            f"Quantile (τ):           {self.quantile:.3f}\n"
            f"Number of observations: {self.n_obs}\n"
            f"Number of lags:         {self.lags}\n"
            f"{'-'*70}\n"
            f"                        Estimates\n"
            f"{'-'*70}\n"
            f"ρ₁(τ) [QR]:             {self.rho_tau:.6f}\n"
            f"ρ₁ [OLS]:               {self.rho_ols:.6f}\n"
            f"α₀(τ):                  {self.alpha_tau:.6f}\n"
            f"δ²:                     {self.delta2:.6f}\n"
            f"Half-life:              {self.half_life}\n"
            f"{'-'*70}\n"
            f"                     Test Statistics\n"
            f"{'-'*70}\n"
            f"tₙ(τ):                  {self.statistic:.4f} {stars}\n"
            f"{coef_line}"
            f"{'-'*70}\n"
            f"                     Critical Values\n"
            f"{'-'*70}\n"
            f"1% critical value:      {self.critical_values['1%']:.4f}\n"
            f"5% critical value:      {self.critical_values['5%']:.4f}\n"
            f"10% critical value:     {self.critical_values['10%']:.4f}\n"
            f"{'='*70}\n"
            f"Note: *** p<0.01, ** p<0.05, * p<0.10\n"
            f"H₀: Unit root (ρ₁ = 1) vs H₁: Stationarity (ρ₁ < 1)\n"
            f"{'='*70}\n"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for export."""
        return {
            'quantile': self.quantile,
            'statistic': self.statistic,
            'coefficient_statistic': self.coefficient_statistic,
            'pvalue': self.pvalue,
            'lags': self.lags,
            'rho_tau': self.rho_tau,
            'rho_ols': self.rho_ols,
            'alpha_tau': self.alpha_tau,
            'delta2': self.delta2,
            'half_life': self.half_life,
            'cv_1pct': self.critical_values['1%'],
            'cv_5pct': self.critical_values['5%'],
            'cv_10pct': self.critical_values['10%'],
            'model': self.model,
            'n_obs': self.n_obs
        }


@dataclass
class QADFProcessResult:
    """
    Container for Quantile ADF process results (multiple quantiles).
    
    Attributes
    ----------
    results : List[QADFResult]
        List of individual QADF results for each quantile.
    qks_alpha : float
        Kolmogorov-Smirnov type statistic based on coefficient.
    qks_t : float
        Kolmogorov-Smirnov type statistic based on t-ratio.
    qcm_alpha : float
        Cramer-von Mises type statistic based on coefficient.
    qcm_t : float
        Cramer-von Mises type statistic based on t-ratio.
    quantiles : np.ndarray
        Array of quantiles used.
    """
    results: List[QADFResult]
    qks_alpha: float
    qks_t: float
    qcm_alpha: float
    qcm_t: float
    quantiles: np.ndarray
    bootstrap_cv: Optional[Dict] = None
    
    def __repr__(self) -> str:
        """String representation of process results."""
        lines = [
            f"\n{'='*80}",
            f"              Quantile ADF Unit Root Test - Process Results",
            f"{'='*80}",
            f"Reference: Koenker, R., Xiao, Z. (2004). JASA, 99, 775-787.",
            f"{'-'*80}",
            f"{'Quantile':>10} {'ρ₁(τ)':>10} {'tₙ(τ)':>12} {'Uₙ(τ)':>12} {'δ²':>10} {'CV(5%)':>10}",
            f"{'-'*80}"
        ]
        
        for res in self.results:
            stars = ''
            if res.statistic < res.critical_values['1%']:
                stars = '***'
            elif res.statistic < res.critical_values['5%']:
                stars = '**'
            elif res.statistic < res.critical_values['10%']:
                stars = '*'
            
            lines.append(
                f"{res.quantile:>10.2f} {res.rho_tau:>10.4f} {res.statistic:>10.4f}{stars:>2} "
                f"{res.coefficient_statistic:>10.4f} {res.delta2:>10.4f} {res.critical_values['5%']:>10.4f}"
            )
        
        lines.extend([
            f"{'-'*80}",
            f"                         Global Test Statistics",
            f"{'-'*80}",
            f"QKS_α (sup|Uₙ(τ)|):     {self.qks_alpha:.4f}",
            f"QKS_t (sup|tₙ(τ)|):     {self.qks_t:.4f}",
            f"QCM_α (∫Uₙ(τ)²dτ):      {self.qcm_alpha:.4f}",
            f"QCM_t (∫tₙ(τ)²dτ):      {self.qcm_t:.4f}",
        ])
        
        if self.bootstrap_cv is not None:
            lines.extend([
                f"{'-'*80}",
                f"Bootstrap Critical Values (5% level):",
                f"  QKS_α: {self.bootstrap_cv.get('qks_alpha_5pct', 'N/A')}",
                f"  QKS_t: {self.bootstrap_cv.get('qks_t_5pct', 'N/A')}",
                f"  QCM_α: {self.bootstrap_cv.get('qcm_alpha_5pct', 'N/A')}",
                f"  QCM_t: {self.bootstrap_cv.get('qcm_t_5pct', 'N/A')}",
            ])
        
        lines.extend([
            f"{'='*80}",
            f"Note: *** p<0.01, ** p<0.05, * p<0.10",
            f"{'='*80}"
        ])
        
        return '\n'.join(lines)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame."""
        records = [res.to_dict() for res in self.results]
        df = pd.DataFrame(records)
        df.set_index('quantile', inplace=True)
        return df


def _check_array(y: Union[np.ndarray, pd.Series]) -> np.ndarray:
    """
    Convert input to numpy array and validate.
    
    Parameters
    ----------
    y : array-like
        Input time series.
    
    Returns
    -------
    np.ndarray
        Validated numpy array.
    """
    if isinstance(y, pd.Series):
        y = y.values
    y = np.asarray(y, dtype=np.float64).flatten()
    
    if np.any(np.isnan(y)):
        raise ValueError("Input series contains NaN values.")
    if len(y) < 20:
        raise ValueError("Input series must have at least 20 observations.")
    
    return y


def _lagmat(x: np.ndarray, maxlag: int) -> np.ndarray:
    """
    Create a matrix of lagged values.
    
    Parameters
    ----------
    x : np.ndarray
        Input array.
    maxlag : int
        Maximum number of lags.
    
    Returns
    -------
    np.ndarray
        Matrix of lagged values with shape (n-maxlag, maxlag).
    """
    n = len(x)
    if maxlag >= n:
        raise ValueError("maxlag must be less than the length of the series.")
    
    result = np.zeros((n - maxlag, maxlag))
    for j in range(maxlag):
        result[:, j] = x[maxlag - j - 1:n - j - 1]
    
    return result


def _adf_lag_selection(y: np.ndarray, pmax: int, ic: str = 'aic') -> Tuple[int, float]:
    """
    Select optimal lag length for ADF regression using information criteria.
    
    This follows the GAUSS implementation approach for proper array alignment.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series.
    pmax : int
        Maximum number of lags to consider.
    ic : str
        Information criterion: 'aic', 'bic', or 't-stat'.
    
    Returns
    -------
    Tuple[int, float]
        Optimal lag and ADF t-statistic.
    """
    n = len(y)
    dy = np.diff(y)
    y1 = y[:-1]
    
    best_ic = np.inf
    best_lag = 0
    best_adf_t = 0.0
    
    for p in range(pmax + 1):
        # Following GAUSS: trim by p+1 from start
        trim_start = p + 1
        y_dep = dy[trim_start:]
        y_lag = y1[trim_start:]
        
        # Build regressor matrix: constant, y_{t-1}
        X = np.column_stack([np.ones(len(y_dep)), y_lag])
        
        if p > 0:
            # Create lagged differences: Δy_{t-1}, Δy_{t-2}, ..., Δy_{t-p}
            # Following GAUSS approach: create lags then trim
            dy_lags = np.zeros((len(dy), p))
            for j in range(1, p + 1):
                dy_lags[j:, j-1] = dy[:-j]
            # Trim to match y_dep
            dy_lags = dy_lags[trim_start:, :]
            X = np.column_stack([X, dy_lags])
        
        # OLS estimation
        try:
            beta = np.linalg.lstsq(X, y_dep, rcond=None)[0]
            resid = y_dep - X @ beta
            ssr = np.sum(resid**2)
            n_eff = len(y_dep)
            k = X.shape[1]
            
            # Calculate standard error of rho coefficient
            sigma2 = ssr / (n_eff - k)
            XtX_inv = np.linalg.inv(X.T @ X)
            se_rho = np.sqrt(sigma2 * XtX_inv[1, 1])
            adf_t = beta[1] / se_rho
            
            # Information criterion
            if ic.lower() == 'aic':
                ic_val = np.log(ssr / n_eff) + 2 * k / n_eff
            elif ic.lower() == 'bic':
                ic_val = np.log(ssr / n_eff) + k * np.log(n_eff) / n_eff
            elif ic.lower() == 't-stat':
                # t-stat significance: include lag if |t| > 1.96
                if p > 0:
                    se_last = np.sqrt(sigma2 * XtX_inv[-1, -1])
                    t_last = abs(beta[-1] / se_last)
                    if t_last < 1.96 and p > 0:
                        ic_val = np.inf
                    else:
                        ic_val = -p  # Prefer higher lag if significant
                else:
                    ic_val = 0
            else:
                raise ValueError(f"Unknown information criterion: {ic}")
            
            if ic_val < best_ic:
                best_ic = ic_val
                best_lag = p
                best_adf_t = adf_t
                
        except np.linalg.LinAlgError:
            continue
    
    return best_lag, best_adf_t


def bandwidth_hs(tau: float, n: int, alpha: float = 0.05) -> float:
    """
    Calculate Hall-Sheather bandwidth for quantile regression.
    
    Reference: Hall, P. and Sheather, S.J. (1988). On the distribution of a 
    studentized quantile. JRSS-B 50(3), 381-391.
    
    Parameters
    ----------
    tau : float
        Quantile level (0 < tau < 1).
    n : int
        Sample size.
    alpha : float
        Significance level.
    
    Returns
    -------
    float
        Bandwidth parameter h.
    """
    x0 = norm.ppf(tau)
    f0 = norm.pdf(x0)
    
    h = (n ** (-1/3) * 
         (norm.ppf(1 - alpha/2) ** (2/3)) * 
         ((1.5 * f0**2) / (2 * x0**2 + 1)) ** (1/3))
    
    return h


def bandwidth_bofinger(tau: float, n: int) -> float:
    """
    Calculate Bofinger bandwidth for quantile regression.
    
    Reference: Bofinger, E. (1975). Estimation of a density function using 
    order statistics. Australian Journal of Statistics, 17, 1-7.
    
    Parameters
    ----------
    tau : float
        Quantile level (0 < tau < 1).
    n : int
        Sample size.
    
    Returns
    -------
    float
        Bandwidth parameter h.
    """
    x0 = norm.ppf(tau)
    f0 = norm.pdf(x0)
    
    h = n ** (-0.2) * ((4.5 * f0**4) / (2 * x0**2 + 1)**2) ** 0.2
    
    return h


def _get_bandwidth(tau: float, n: int, alpha: float = 0.05) -> float:
    """
    Calculate optimal bandwidth with boundary adjustments.
    
    This function implements the bandwidth selection procedure from the
    original GAUSS code, including adjustments for extreme quantiles.
    
    Parameters
    ----------
    tau : float
        Quantile level.
    n : int
        Sample size.
    alpha : float
        Significance level.
    
    Returns
    -------
    float
        Adjusted bandwidth.
    """
    h = bandwidth_hs(tau, n, alpha)
    
    if tau <= 0.5 and h > tau:
        h = bandwidth_bofinger(tau, n)
        if h > tau:
            h = tau / 1.5
    
    if tau > 0.5 and h > 1 - tau:
        h = bandwidth_bofinger(tau, n)
        if h > (1 - tau):
            h = (1 - tau) / 1.5
    
    return h


def _quantile_regression(y: np.ndarray, X: np.ndarray, tau: float,
                         max_iter: int = 1000, tol: float = 1e-8) -> Tuple[np.ndarray, np.ndarray]:
    """
    Quantile regression using the interior point method.
    
    This implements the Barrodale-Roberts algorithm variant for
    solving the quantile regression problem.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    X : np.ndarray
        Design matrix.
    tau : float
        Quantile level.
    max_iter : int
        Maximum number of iterations.
    tol : float
        Convergence tolerance.
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Estimated coefficients and residuals.
    """
    try:
        from statsmodels.regression.quantile_regression import QuantReg
        model = QuantReg(y, X)
        result = model.fit(q=tau, max_iter=max_iter)
        return result.params, result.resid
    except ImportError:
        # Fallback to simple iteratively reweighted least squares
        n, k = X.shape
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        
        for _ in range(max_iter):
            resid = y - X @ beta
            weights = np.where(resid >= 0, tau, 1 - tau) / (np.abs(resid) + 1e-10)
            W = np.diag(weights)
            beta_new = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
            
            if np.max(np.abs(beta_new - beta)) < tol:
                break
            beta = beta_new
        
        resid = y - X @ beta
        return beta, resid


def _get_critical_values_hansen(delta2: float, model: str) -> Dict[str, float]:
    """
    Get critical values from Hansen (1995) table for CADF test.
    
    The critical values are interpolated based on δ² (delta squared).
    
    Reference: Hansen, B. (1995). Rethinking the Univariate Approach to Unit
    Root Tests: How to Use Covariates to Increase Power. Econometric Theory,
    11, 1148-1171.
    
    Parameters
    ----------
    delta2 : float
        The nuisance parameter δ² (squared long-run correlation).
    model : str
        Model type: 'nc' (no constant), 'c' (constant), 'ct' (constant + trend).
    
    Returns
    -------
    Dict[str, float]
        Dictionary with critical values at 1%, 5%, and 10% levels.
    """
    # Critical values from Hansen (1995), Table II
    # Rows correspond to δ² = 0.1, 0.2, ..., 1.0
    
    # No constant model
    cv_nc = np.array([
        [-2.4611512, -1.7832090, -1.4189957],
        [-2.4943410, -1.8184897, -1.4589747],
        [-2.5152783, -1.8516957, -1.5071775],
        [-2.5509773, -1.8957720, -1.5323511],
        [-2.5520784, -1.8949965, -1.5418830],
        [-2.5490848, -1.8981677, -1.5625462],
        [-2.5547456, -1.9343180, -1.5889045],
        [-2.5761273, -1.9387996, -1.6020210],
        [-2.5511921, -1.9328373, -1.6128210],
        [-2.5658000, -1.9393000, -1.6156000]
    ])
    
    # Constant model
    cv_c = np.array([
        [-2.7844267, -2.1158290, -1.7525193],
        [-2.9138762, -2.2790427, -1.9172046],
        [-3.0628184, -2.3994711, -2.0573070],
        [-3.1376157, -2.5070473, -2.1680520],
        [-3.1914660, -2.5841611, -2.2520173],
        [-3.2437157, -2.6399560, -2.3163270],
        [-3.2951006, -2.7180169, -2.4085640],
        [-3.3627161, -2.7536756, -2.4577709],
        [-3.3896556, -2.8074982, -2.5037759],
        [-3.4336000, -2.8621000, -2.5671000]
    ])
    
    # Constant and trend model
    cv_ct = np.array([
        [-2.9657928, -2.3081543, -1.9519926],
        [-3.1929596, -2.5482619, -2.1991651],
        [-3.3727717, -2.7283918, -2.3806008],
        [-3.4904849, -2.8669056, -2.5315918],
        [-3.6003166, -2.9853079, -2.6672416],
        [-3.6819803, -3.0954760, -2.7815263],
        [-3.7551759, -3.1783550, -2.8728146],
        [-3.8348596, -3.2674954, -2.9735550],
        [-3.8800989, -3.3316415, -3.0364171],
        [-3.9638000, -3.4126000, -3.1279000]
    ])
    
    # Select appropriate table
    if model == 'nc':
        cv_table = cv_nc
    elif model == 'c':
        cv_table = cv_c
    elif model == 'ct':
        cv_table = cv_ct
    else:
        raise ValueError(f"Unknown model type: {model}. Use 'nc', 'c', or 'ct'.")
    
    # Interpolation based on delta2
    # The table is indexed by delta2 = 0.1, 0.2, ..., 1.0
    if delta2 < 0.1:
        cv = cv_table[0, :]
    elif delta2 >= 1.0:
        cv = cv_table[9, :]
    else:
        # Linear interpolation
        r210 = delta2 * 10
        r2a = int(np.floor(r210))
        r2b = int(np.ceil(r210))
        
        if r2a == r2b:
            cv = cv_table[r2a - 1, :]
        else:
            wa = r2b - r210
            cv = wa * cv_table[r2a - 1, :] + (1 - wa) * cv_table[r2b - 1, :]
    
    return {
        '1%': float(cv[0]),
        '5%': float(cv[1]),
        '10%': float(cv[2])
    }


def _calculate_delta2(y: np.ndarray, X_full: np.ndarray, dy: np.ndarray,
                      tau: float, qr_beta: np.ndarray,
                      use_fourier: bool = False) -> float:
    """
    Calculate the nuisance parameter δ² (delta squared).
    
    This is the squared long-run correlation coefficient between
    {w_t} and {ψ_τ(u_{tτ})}, as defined in Section 3.1 of
    Koenker & Xiao (2004).
    
    Following the GAUSS implementation exactly:
        res = y - (ones(rows(x),1)~x) * qr_beta
        ind = res .< 0
        phi = tau - ind
        cov = sumc((w - meanc(w)) .* (phi - meanc(phi)))/(rows(w) - 1)
        delta2 = (cov/(stdc(w) * sqrt(tau * (1-tau))))^2
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    X_full : np.ndarray
        Full design matrix including constant (already with constant as first column).
    dy : np.ndarray
        First difference of the original series (w in GAUSS code).
    tau : float
        Quantile level.
    qr_beta : np.ndarray
        Quantile regression coefficients from QR estimation.
    use_fourier : bool
        Whether Fourier terms are included (use residuals as w).
    
    Returns
    -------
    float
        The δ² parameter (squared long-run correlation).
    """
    # Calculate residuals: res = y - X * qr_beta
    # X_full should already be the full design matrix with constant
    resid = y - X_full @ qr_beta
    
    # Indicator for negative residuals: ind = res < 0
    ind = (resid < 0).astype(float)
    
    # ψ_τ(u) = τ - I(u < 0)
    phi = tau - ind
    
    # Use dy for covariance calculation (unless Fourier terms are used)
    # In GAUSS: if ismiss(w) then w = res else w = dy
    if use_fourier:
        w = resid
    else:
        w = dy
    
    # Ensure w and phi have the same length
    min_len = min(len(w), len(phi))
    w = w[-min_len:]
    phi = phi[-min_len:]
    
    # Calculate covariance (sample covariance with ddof=1)
    # GAUSS: cov = sumc((w - meanc(w)) .* (phi - meanc(phi)))/(rows(w) - 1)
    w_centered = w - np.mean(w)
    phi_centered = phi - np.mean(phi)
    cov = np.sum(w_centered * phi_centered) / (len(w) - 1)
    
    # Calculate δ²
    # GAUSS: delta2 = (cov/(stdc(w) * sqrt(tau * (1-tau))))^2
    std_w = np.std(w, ddof=1)
    if std_w < 1e-10:
        std_w = 1e-10  # Avoid division by zero
    
    delta2 = (cov / (std_w * np.sqrt(tau * (1 - tau)))) ** 2
    
    return delta2


def _calculate_qadf_statistic(y: np.ndarray, y1: np.ndarray, 
                               dyl: Optional[np.ndarray], X: np.ndarray,
                               rho_tau: float, tau: float, n: int, p: int,
                               model: str = 'c',
                               use_fourier: bool = False) -> float:
    """
    Calculate the QADF t-statistic.
    
    This implements equation (9) from Koenker & Xiao (2004):
    
    t_n(τ) = f(F^{-1}(τ)) / √(τ(1-τ)) * √(Y'_{-1} P_X Y_{-1}) * (ρ̂₁(τ) - 1)
    
    where P_X is the projection matrix onto the orthogonal complement of X.
    
    Following GAUSS code exactly:
        h = __get_qr_adf_h(tau, n);
        rq1 = __get_qr_adf_beta(y, x, tau+h);
        rq2 = __get_qr_adf_beta(y, x, tau-h);
        z = ones(rows(x), 1)~x;
        mz = meanc(z);
        q1 = mz' * rq1;
        q2 = mz' * rq2;
        fz = 2 * h/(q1 - q2);
        
        xx = ones(rows(x), 1);
        if p > 0 then xx = ones(rows(x), 1)~dyl; endif;
        PX = eye(rows(xx)) - xx * inv(xx'xx) * xx';
        QURadf = fz/sqrt(tau * (1 - tau)) * sqrt(Y1' * PX * Y1) * (rho_tau -1);
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    y1 : np.ndarray
        Lagged dependent variable y_{t-1}.
    dyl : np.ndarray or None
        Matrix of lagged first differences.
    X : np.ndarray
        Design matrix WITHOUT constant (y_{t-1}, Δy lags, trend if ct).
    rho_tau : float
        Estimated autoregressive coefficient at quantile τ.
    tau : float
        Quantile level.
    n : int
        Sample size.
    p : int
        Number of lags.
    model : str
        Model type ('c' or 'ct').
    use_fourier : bool
        Whether Fourier terms are used.
    
    Returns
    -------
    float
        The QADF t-statistic.
    """
    # Get bandwidth following GAUSS: h = __get_qr_adf_h(tau, n)
    h = _get_bandwidth(tau, n)
    
    # Ensure tau ± h stays in valid range [0, 1]
    tau_upper = min(tau + h, 0.999)
    tau_lower = max(tau - h, 0.001)
    
    # Following GAUSS: z = ones(rows(x), 1)~x (add constant)
    # X passed here is WITHOUT constant, so we need to add it
    X_with_const = np.column_stack([np.ones(len(y)), X])
    
    # Get beta from quantile regression at tau+h and tau-h
    # Following GAUSS: rq1 = __get_qr_adf_beta(y, x, tau+h)
    rq1, _ = _quantile_regression(y, X_with_const, tau_upper)
    rq2, _ = _quantile_regression(y, X_with_const, tau_lower)
    
    # Calculate density estimate f(F^{-1}(τ))
    # GAUSS: z = ones(rows(x), 1)~x; mz = meanc(z); q1 = mz' * rq1; q2 = mz' * rq2
    z = X_with_const
    mz = np.mean(z, axis=0)
    
    q1 = np.dot(mz, rq1)
    q2 = np.dot(mz, rq2)
    
    # GAUSS: fz = 2 * h/(q1 - q2); if fz < 0 then fz = 0.01; endif
    fz = 2 * h / (q1 - q2) if (q1 - q2) != 0 else 0.01
    if fz < 0:
        fz = 0.01
    
    # Build the projection matrix P_X
    # GAUSS: xx = ones(rows(x), 1); if p > 0 then xx = ones(rows(x), 1)~dyl; endif
    # Note: xx does NOT include y_{t-1}, only constant and Δy lags
    xx = np.ones((len(y), 1))
    
    if use_fourier:
        # Include Fourier terms but not y_{t-1}
        # GAUSS: xx = xx~x[.,2:cols(x)];
        if X.shape[1] > 1:
            xx = np.column_stack([xx, X[:, 1:]])  # Skip y_{t-1}
    else:
        if p > 0 and dyl is not None:
            # GAUSS: xx = ones(rows(x), 1)~dyl
            xx = np.column_stack([xx, dyl])
        
        if model == 'ct':
            # Include trend for 'ct' model
            trend = np.arange(1, len(y) + 1).reshape(-1, 1)
            xx = np.column_stack([xx, trend])
    
    # Projection matrix: P_X = I - X(X'X)^{-1}X'
    # GAUSS: PX = eye(rows(xx)) - xx * inv(xx'xx) * xx';
    try:
        XtX_inv = np.linalg.inv(xx.T @ xx)
        PX = np.eye(len(xx)) - xx @ XtX_inv @ xx.T
    except np.linalg.LinAlgError:
        XtX_inv = np.linalg.pinv(xx.T @ xx)
        PX = np.eye(len(xx)) - xx @ XtX_inv @ xx.T
    
    # Ensure y1 has the correct shape
    y1_vec = y1.flatten() if y1.ndim > 1 else y1
    if len(y1_vec) > len(y):
        y1_vec = y1_vec[-len(y):]
    elif len(y1_vec) < len(y):
        # Pad from front with first value
        y1_vec = np.concatenate([np.full(len(y) - len(y1_vec), y1_vec[0]), y1_vec])
    
    # Calculate √(Y'_{-1} P_X Y_{-1})
    # GAUSS: sqrt(Y1' * PX * Y1)
    y1_proj = y1_vec @ PX @ y1_vec
    
    if y1_proj <= 0:
        y1_proj = 1e-10  # Numerical stability
    
    # Calculate QADF statistic
    # GAUSS: QURadf = fz/sqrt(tau * (1 - tau)) * sqrt(Y1' * PX * Y1) * (rho_tau -1)
    qadf = (fz / np.sqrt(tau * (1 - tau))) * np.sqrt(y1_proj) * (rho_tau - 1)
    
    return qadf


def qadf(y: Union[np.ndarray, pd.Series],
         tau: float = 0.5,
         model: str = 'c',
         pmax: int = 8,
         ic: str = 'aic',
         verbose: bool = True) -> QADFResult:
    """
    Perform the Quantile ADF unit root test.
    
    This function implements the unit root test proposed by Koenker & Xiao (2004)
    for testing the null hypothesis of a unit root against the alternative of
    stationarity at a specific quantile.
    
    Parameters
    ----------
    y : array-like
        The time series data (N×1 vector).
    tau : float, default 0.5
        The quantile at which to perform the test (0 < tau < 1).
    model : str, default 'c'
        Model specification:
        - 'c': Constant only (default in Koenker & Xiao, 2004)
        - 'ct': Constant and linear trend
    pmax : int, default 8
        Maximum number of lags for Δy in the ADF regression.
    ic : str, default 'aic'
        Information criterion for lag selection:
        - 'aic': Akaike Information Criterion
        - 'bic': Schwarz Bayesian Information Criterion
        - 't-stat': Sequential t-statistic significance
    verbose : bool, default True
        If True, print results.
    
    Returns
    -------
    QADFResult
        A dataclass containing test statistics, critical values, and estimates.
    
    Notes
    -----
    The test statistic follows the limiting distribution given in equation (9)
    of Koenker & Xiao (2004):
    
        t_n(τ) → δ(∫₀¹ W̄₁²)^{-1/2} ∫₀¹ W̄₁ dW₁ + √(1-δ²) N(0,1)
    
    which is a mixture of the Dickey-Fuller distribution and the standard
    normal, with weights determined by δ (the long-run correlation coefficient).
    
    References
    ----------
    Koenker, R., Xiao, Z. (2004). Unit Root Quantile Autoregression Inference.
    Journal of the American Statistical Association, 99, 775-787.
    
    Examples
    --------
    >>> import numpy as np
    >>> from qadf import qadf
    >>> # Generate a random walk
    >>> np.random.seed(42)
    >>> y = np.cumsum(np.random.randn(200))
    >>> result = qadf(y, tau=0.5, model='c')
    >>> print(result)
    """
    # Validate inputs
    if not 0 < tau < 1:
        raise ValueError("Quantile tau must be between 0 and 1 (exclusive).")
    
    if model not in ['c', 'ct', 'nc']:
        raise ValueError("Model must be 'c' (constant), 'ct' (constant+trend), or 'nc' (no constant).")
    
    # Convert and validate data
    y = _check_array(y)
    n_original = len(y)
    
    # Determine optimal lag using ADF
    p, adf_t = _adf_lag_selection(y, pmax, ic)
    
    # Following GAUSS code structure exactly:
    # In GAUSS:
    #   dy = y[t] - y[t-1]  (first difference)
    #   y1 = y[t-1]         (lagged level)
    #   y is the dependent variable y[t]
    #
    # After trimming by (p+1) from start:
    #   y[t] for t = p+2, p+3, ..., n
    #   y1[t-1] for same t values
    #   Δy lags for same t values
    
    n_orig = len(y)
    
    # Create first difference: Δy_t = y_t - y_{t-1}
    dy = np.diff(y)  # Length: n_orig - 1
    
    # Number of observations after trimming
    trim_start = p + 1
    n_eff = n_orig - trim_start
    
    # Dependent variable: y_t for t = trim_start+1, ..., n_orig (0-indexed: trim_start to n_orig-1)
    y_dep = y[trim_start:]  # Length: n_orig - trim_start
    
    # Lagged level: y_{t-1} for same t values
    # y_{t-1} where t = trim_start+1, ..., n_orig means indices trim_start-1 to n_orig-2 of original y
    y_lag = y[trim_start-1:-1]  # Length: n_orig - trim_start
    
    # Build regressor matrix starting with lagged level
    X = y_lag.reshape(-1, 1)
    
    # Create lagged differences if p > 0
    # We need Δy_{t-1}, Δy_{t-2}, ..., Δy_{t-p} for each observation
    # where t corresponds to the index in y_dep
    #
    # y_dep[i] corresponds to y at time trim_start+i (0-indexed)
    # y_lag[i] corresponds to y at time trim_start+i-1
    # Δy_{t-1} for y_dep[i] = Δy at time (trim_start+i-1)
    #                       = y[trim_start+i-1] - y[trim_start+i-2]
    #                       = dy[trim_start+i-2]
    # So for j=1 (Δy_{t-1}): we need dy[trim_start-2 + i] for i=0,1,...,n_eff-1
    # For j=2 (Δy_{t-2}): we need dy[trim_start-3 + i]
    # General: for j, start_idx = trim_start - 1 - j
    if p > 0:
        dyl = np.zeros((n_eff, p))
        for j in range(1, p + 1):
            # Δy_{t-j} for observation i is dy at index (trim_start + i - 1 - j)
            # = dy[trim_start - 1 - j + i] for i = 0, ..., n_eff-1
            start_idx = trim_start - 1 - j
            dyl[:, j-1] = dy[start_idx:start_idx + n_eff]
        X = np.column_stack([X, dyl])
        # dy_trimmed = Δy_t for the dependent variable observations
        # For y_dep[i] = y at time trim_start+i, Δy_t = y[trim_start+i] - y[trim_start+i-1] = dy[trim_start+i-1]
        # So dy_trimmed starts at dy[trim_start-1] and has n_eff elements
        # But we need to be careful: dy has length n_orig-1, and we need indices trim_start-1 to trim_start-1+n_eff-1
        # Let's verify: trim_start + n_eff = trim_start + (n_orig - trim_start) = n_orig
        # So we need dy[trim_start-1 : n_orig-1], which has length n_orig - 1 - (trim_start-1) = n_orig - trim_start = n_eff ✓
        dy_trimmed = dy[trim_start-1:trim_start-1 + n_eff]
    else:
        dyl = None
        # When p=0, trim_start = 1, so dy_trimmed = dy[0:n_orig-1] = dy (all of it)
        # Actually with p=0: n_eff = n_orig - 1, dy has n_orig-1 elements
        # dy_trimmed should have n_eff elements starting from dy[trim_start-1] = dy[0]
        dy_trimmed = dy[:n_eff]
    
    # Add trend if model='ct'
    if model == 'ct':
        trend = np.arange(1, n_eff + 1).reshape(-1, 1)
        X = np.column_stack([X, trend])
    
    # Add constant as first column (GAUSS: ones(rows(x),1) ~ x)
    X = np.column_stack([np.ones(n_eff), X])
    
    n = n_eff
    
    # Quantile regression
    qr_beta, qr_resid = _quantile_regression(y_dep, X, tau)
    
    # Extract coefficients
    alpha_tau = qr_beta[0]  # Intercept
    rho_tau = qr_beta[1]    # Coefficient on y_{t-1}
    
    # OLS for comparison
    ols_beta = np.linalg.lstsq(X, y_dep, rcond=None)[0]
    rho_ols = ols_beta[1]
    
    # Calculate δ² (delta squared)
    # Pass full X matrix (with constant) to _calculate_delta2
    delta2 = _calculate_delta2(y_dep, X, dy_trimmed, tau, qr_beta)
    
    # Bound delta2 to valid range
    delta2 = np.clip(delta2, 0.01, 0.99)
    
    # Calculate QADF statistic
    qadf_stat = _calculate_qadf_statistic(
        y_dep, y_lag, dyl, X[:, 1:], rho_tau, tau, n, p, model
    )
    
    # Get critical values
    cv = _get_critical_values_hansen(delta2, model)
    
    # Calculate half-life
    if rho_tau >= 1 or rho_tau <= 0:
        half_life = '∞'
    else:
        hl = np.log(0.5) / np.log(abs(rho_tau))
        half_life = hl if hl > 0 else '∞'
    
    # Coefficient-based statistic U_n(τ) = n(α̂₁(τ) - 1)
    coef_stat = n * (rho_tau - 1)
    
    # Create result object
    result = QADFResult(
        statistic=qadf_stat,
        pvalue=None,  # Would require bootstrap
        quantile=tau,
        lags=p,
        rho_tau=rho_tau,
        rho_ols=rho_ols,
        alpha_tau=alpha_tau,
        delta2=delta2,
        critical_values=cv,
        model=model,
        n_obs=n,
        half_life=half_life,
        coefficient_statistic=coef_stat
    )
    
    if verbose:
        print(result)
    
    return result


def qadf_process(y: Union[np.ndarray, pd.Series],
                 quantiles: Optional[np.ndarray] = None,
                 model: str = 'c',
                 pmax: int = 8,
                 ic: str = 'aic',
                 verbose: bool = True) -> QADFProcessResult:
    """
    Perform the QADF test over a range of quantiles.
    
    This function computes the QADF test at multiple quantiles and
    calculates global test statistics (QKS and QCM) as described in
    Section 3.3 of Koenker & Xiao (2004).
    
    Parameters
    ----------
    y : array-like
        The time series data.
    quantiles : array-like, optional
        Array of quantiles to test. Default is [0.1, 0.2, ..., 0.9].
    model : str, default 'c'
        Model specification ('c' or 'ct').
    pmax : int, default 8
        Maximum number of lags.
    ic : str, default 'aic'
        Information criterion for lag selection.
    verbose : bool, default True
        If True, print results.
    
    Returns
    -------
    QADFProcessResult
        Results containing individual quantile tests and global statistics.
    
    Notes
    -----
    The global test statistics are:
    
    - QKS_α = sup_{τ∈T} |U_n(τ)|
    - QKS_t = sup_{τ∈T} |t_n(τ)|
    - QCM_α = ∫_{τ∈T} U_n(τ)² dτ
    - QCM_t = ∫_{τ∈T} t_n(τ)² dτ
    
    References
    ----------
    Koenker, R., Xiao, Z. (2004). Unit Root Quantile Autoregression Inference.
    Journal of the American Statistical Association, 99, 775-787.
    
    Examples
    --------
    >>> import numpy as np
    >>> from qadf import qadf_process
    >>> np.random.seed(42)
    >>> y = np.cumsum(np.random.randn(200))
    >>> result = qadf_process(y)
    >>> df = result.to_dataframe()
    """
    if quantiles is None:
        quantiles = np.arange(0.1, 1.0, 0.1)
    
    quantiles = np.asarray(quantiles)
    
    # Validate quantiles
    if np.any(quantiles <= 0) or np.any(quantiles >= 1):
        raise ValueError("All quantiles must be strictly between 0 and 1.")
    
    # Run QADF at each quantile
    results = []
    for tau in quantiles:
        res = qadf(y, tau=tau, model=model, pmax=pmax, ic=ic, verbose=False)
        results.append(res)
    
    # Calculate global test statistics
    t_stats = np.array([r.statistic for r in results])
    u_stats = np.array([r.coefficient_statistic for r in results])
    
    # KS-type statistics (supremum)
    qks_alpha = np.max(np.abs(u_stats))
    qks_t = np.max(np.abs(t_stats))
    
    # CM-type statistics (integral approximation using trapezoidal rule)
    dtau = np.diff(quantiles)
    dtau = np.append(dtau, dtau[-1])  # Extend to same length
    
    qcm_alpha = np.sum(u_stats**2 * dtau)
    qcm_t = np.sum(t_stats**2 * dtau)
    
    result = QADFProcessResult(
        results=results,
        qks_alpha=qks_alpha,
        qks_t=qks_t,
        qcm_alpha=qcm_alpha,
        qcm_t=qcm_t,
        quantiles=quantiles
    )
    
    if verbose:
        print(result)
    
    return result


# Alias for compatibility with original naming
qr_adf = qadf
quantileADF = qadf
QRADF = qadf
