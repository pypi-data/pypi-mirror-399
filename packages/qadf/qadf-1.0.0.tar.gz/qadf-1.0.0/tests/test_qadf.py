"""
Test Suite for QADF Package
============================

Comprehensive tests for the Quantile ADF Unit Root Test implementation.

Author: Dr Merwan Roudane
"""

import numpy as np
import pandas as pd
import pytest
from scipy import stats


# Skip tests if qadf not installed
pytest.importorskip("qadf")

from qadf import (
    qadf,
    qadf_process,
    QADFResult,
    QADFProcessResult,
    get_hansen_critical_values,
    get_critical_values_table,
    bandwidth_hs,
    bandwidth_bofinger,
    bootstrap_critical_values,
    generate_bootstrap_sample,
)


class TestBasicFunctionality:
    """Test basic functionality of QADF test."""
    
    @pytest.fixture
    def random_walk(self):
        """Generate a random walk for testing."""
        np.random.seed(42)
        return np.cumsum(np.random.randn(200))
    
    @pytest.fixture
    def stationary_series(self):
        """Generate a stationary AR(1) series."""
        np.random.seed(42)
        n = 200
        y = np.zeros(n)
        for t in range(1, n):
            y[t] = 0.5 * y[t-1] + np.random.randn()
        return y
    
    def test_qadf_returns_result_object(self, random_walk):
        """Test that qadf returns a QADFResult object."""
        result = qadf(random_walk, tau=0.5, verbose=False)
        assert isinstance(result, QADFResult)
    
    def test_qadf_attributes(self, random_walk):
        """Test that QADFResult has all required attributes."""
        result = qadf(random_walk, tau=0.5, verbose=False)
        
        assert hasattr(result, 'statistic')
        assert hasattr(result, 'quantile')
        assert hasattr(result, 'lags')
        assert hasattr(result, 'rho_tau')
        assert hasattr(result, 'rho_ols')
        assert hasattr(result, 'delta2')
        assert hasattr(result, 'critical_values')
        assert hasattr(result, 'model')
        assert hasattr(result, 'n_obs')
    
    def test_qadf_quantile_range(self, random_walk):
        """Test that qadf works for valid quantiles."""
        for tau in [0.1, 0.25, 0.5, 0.75, 0.9]:
            result = qadf(random_walk, tau=tau, verbose=False)
            assert result.quantile == tau
    
    def test_qadf_invalid_quantile(self, random_walk):
        """Test that invalid quantiles raise errors."""
        with pytest.raises(ValueError):
            qadf(random_walk, tau=0.0)
        
        with pytest.raises(ValueError):
            qadf(random_walk, tau=1.0)
        
        with pytest.raises(ValueError):
            qadf(random_walk, tau=-0.1)
    
    def test_qadf_models(self, random_walk):
        """Test different model specifications."""
        result_c = qadf(random_walk, tau=0.5, model='c', verbose=False)
        result_ct = qadf(random_walk, tau=0.5, model='ct', verbose=False)
        
        assert result_c.model == 'c'
        assert result_ct.model == 'ct'
    
    def test_qadf_critical_values(self, random_walk):
        """Test that critical values are properly ordered."""
        result = qadf(random_walk, tau=0.5, verbose=False)
        cv = result.critical_values
        
        assert cv['1%'] < cv['5%'] < cv['10%']
    
    def test_rho_tau_near_one_for_random_walk(self, random_walk):
        """Test that ρ(τ) is near 1 for a random walk."""
        result = qadf(random_walk, tau=0.5, verbose=False)
        assert 0.9 < result.rho_tau < 1.1
    
    def test_rho_tau_less_than_one_for_stationary(self, stationary_series):
        """Test that ρ(τ) is less than 1 for stationary series."""
        result = qadf(stationary_series, tau=0.5, verbose=False)
        assert result.rho_tau < 1.0


class TestQADFProcess:
    """Test QADF process over multiple quantiles."""
    
    @pytest.fixture
    def random_walk(self):
        np.random.seed(42)
        return np.cumsum(np.random.randn(200))
    
    def test_qadf_process_returns_result(self, random_walk):
        """Test that qadf_process returns proper result."""
        result = qadf_process(random_walk, verbose=False)
        assert isinstance(result, QADFProcessResult)
    
    def test_qadf_process_default_quantiles(self, random_walk):
        """Test default quantiles (0.1, 0.2, ..., 0.9)."""
        result = qadf_process(random_walk, verbose=False)
        assert len(result.results) == 9
        assert len(result.quantiles) == 9
    
    def test_qadf_process_custom_quantiles(self, random_walk):
        """Test custom quantiles."""
        quantiles = np.array([0.25, 0.5, 0.75])
        result = qadf_process(random_walk, quantiles=quantiles, verbose=False)
        assert len(result.results) == 3
    
    def test_global_statistics(self, random_walk):
        """Test that global statistics are computed."""
        result = qadf_process(random_walk, verbose=False)
        
        assert result.qks_alpha > 0
        assert result.qks_t > 0
        assert result.qcm_alpha > 0
        assert result.qcm_t > 0
    
    def test_to_dataframe(self, random_walk):
        """Test DataFrame conversion."""
        result = qadf_process(random_walk, verbose=False)
        df = result.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(result.results)


class TestCriticalValues:
    """Test critical value functions."""
    
    def test_hansen_cv_model_c(self):
        """Test Hansen critical values for constant model."""
        cv = get_hansen_critical_values(0.5, model='c')
        
        assert '1%' in cv
        assert '5%' in cv
        assert '10%' in cv
        assert cv['1%'] < cv['5%'] < cv['10%']
    
    def test_hansen_cv_model_ct(self):
        """Test Hansen critical values for constant + trend model."""
        cv = get_hansen_critical_values(0.5, model='ct')
        
        # CT model should have more negative CVs than C model
        cv_c = get_hansen_critical_values(0.5, model='c')
        assert cv['5%'] < cv_c['5%']
    
    def test_hansen_cv_interpolation(self):
        """Test that interpolation works for intermediate δ² values."""
        cv1 = get_hansen_critical_values(0.15, model='c')
        cv2 = get_hansen_critical_values(0.10, model='c')
        cv3 = get_hansen_critical_values(0.20, model='c')
        
        # Critical values are negative and become more negative as δ² increases
        # So cv3 < cv1 < cv2 (where '<' means more negative = more extreme)
        # But we need to check that interpolation gives a value between the bounds
        # cv1['5%'] should be between cv2['5%'] and cv3['5%'] numerically
        assert min(cv2['5%'], cv3['5%']) <= cv1['5%'] <= max(cv2['5%'], cv3['5%'])
    
    def test_hansen_cv_boundary(self):
        """Test boundary cases for δ²."""
        cv_low = get_hansen_critical_values(0.01, model='c')
        cv_high = get_hansen_critical_values(0.99, model='c')
        
        assert cv_low['5%'] is not None
        assert cv_high['5%'] is not None
    
    def test_critical_values_table(self):
        """Test critical values table generation."""
        df = get_critical_values_table(model='c')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10  # 10 rows for δ² = 0.1, ..., 1.0


class TestBandwidth:
    """Test bandwidth functions."""
    
    def test_hs_bandwidth_positive(self):
        """Test that Hall-Sheather bandwidth is positive."""
        for tau in [0.1, 0.25, 0.5, 0.75, 0.9]:
            for n in [100, 200, 500]:
                h = bandwidth_hs(tau, n)
                assert h > 0
    
    def test_bofinger_bandwidth_positive(self):
        """Test that Bofinger bandwidth is positive."""
        for tau in [0.1, 0.25, 0.5, 0.75, 0.9]:
            for n in [100, 200, 500]:
                h = bandwidth_bofinger(tau, n)
                assert h > 0
    
    def test_bandwidth_decreases_with_n(self):
        """Test that bandwidth decreases with sample size."""
        h_100 = bandwidth_hs(0.5, 100)
        h_200 = bandwidth_hs(0.5, 200)
        h_500 = bandwidth_hs(0.5, 500)
        
        assert h_100 > h_200 > h_500


class TestBootstrap:
    """Test bootstrap functions."""
    
    @pytest.fixture
    def random_walk(self):
        np.random.seed(42)
        return np.cumsum(np.random.randn(100))
    
    def test_generate_bootstrap_sample(self, random_walk):
        """Test bootstrap sample generation."""
        y_star = generate_bootstrap_sample(random_walk, p=1, random_state=42)
        
        assert len(y_star) == len(random_walk)
        assert y_star[0] == random_walk[0]  # First value preserved
    
    def test_bootstrap_reproducibility(self, random_walk):
        """Test that bootstrap is reproducible with seed."""
        y_star1 = generate_bootstrap_sample(random_walk, p=1, random_state=42)
        y_star2 = generate_bootstrap_sample(random_walk, p=1, random_state=42)
        
        np.testing.assert_array_equal(y_star1, y_star2)
    
    @pytest.mark.slow
    def test_bootstrap_critical_values(self, random_walk):
        """Test bootstrap critical value computation."""
        cv = bootstrap_critical_values(
            random_walk, tau=0.5, model='c', p=1,
            n_replications=100, random_state=42
        )
        
        assert 't_stat' in cv
        assert 'coef_stat' in cv
        assert '5%' in cv['t_stat']


class TestNumericalStability:
    """Test numerical stability."""
    
    def test_extreme_values(self):
        """Test with extreme values."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200)) * 1e6  # Large values
        
        result = qadf(y, tau=0.5, verbose=False)
        assert np.isfinite(result.statistic)
    
    def test_near_zero_variance(self):
        """Test with near-zero variance series."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200) * 1e-6)  # Small variance
        
        result = qadf(y, tau=0.5, verbose=False)
        assert np.isfinite(result.statistic)
    
    def test_constant_series(self):
        """Test that constant series produces warnings or handles gracefully."""
        y = np.ones(200)
        
        # Constant series may not raise but will produce warnings and odd results
        import warnings
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            try:
                result = qadf(y, tau=0.5, verbose=False)
                # If it doesn't raise, check that result has some reasonable structure
                assert hasattr(result, 'statistic')
            except (ValueError, np.linalg.LinAlgError):
                # Either way is acceptable
                pass


class TestInputValidation:
    """Test input validation."""
    
    def test_short_series(self):
        """Test that short series raises error."""
        y = np.random.randn(10)
        
        with pytest.raises(ValueError):
            qadf(y, tau=0.5, verbose=False)
    
    def test_nan_values(self):
        """Test that NaN values raise error."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        y[100] = np.nan
        
        with pytest.raises(ValueError):
            qadf(y, tau=0.5, verbose=False)
    
    def test_invalid_model(self):
        """Test that invalid model raises error."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        
        with pytest.raises(ValueError):
            qadf(y, tau=0.5, model='invalid', verbose=False)
    
    def test_pandas_series_input(self):
        """Test that pandas Series input works."""
        np.random.seed(42)
        y = pd.Series(np.cumsum(np.random.randn(200)))
        
        result = qadf(y, tau=0.5, verbose=False)
        assert isinstance(result, QADFResult)


class TestResultMethods:
    """Test result object methods."""
    
    @pytest.fixture
    def result(self):
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        return qadf(y, tau=0.5, verbose=False)
    
    @pytest.fixture
    def process_result(self):
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        return qadf_process(y, verbose=False)
    
    def test_result_repr(self, result):
        """Test string representation."""
        repr_str = repr(result)
        assert 'Quantile ADF' in repr_str
        assert 'Critical Values' in repr_str
    
    def test_result_to_dict(self, result):
        """Test conversion to dictionary."""
        d = result.to_dict()
        
        assert isinstance(d, dict)
        assert 'statistic' in d
        assert 'quantile' in d
    
    def test_process_to_dataframe(self, process_result):
        """Test process result DataFrame conversion."""
        df = process_result.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert 'rho_tau' in df.columns
        assert 'statistic' in df.columns


# Parametrized tests
class TestParametrized:
    """Parametrized tests for comprehensive coverage."""
    
    @pytest.mark.parametrize("tau", [0.1, 0.25, 0.5, 0.75, 0.9])
    def test_various_quantiles(self, tau):
        """Test various quantile values."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        
        result = qadf(y, tau=tau, verbose=False)
        assert result.quantile == tau
    
    @pytest.mark.parametrize("model", ['c', 'ct'])
    def test_various_models(self, model):
        """Test various model specifications."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        
        result = qadf(y, tau=0.5, model=model, verbose=False)
        assert result.model == model
    
    @pytest.mark.parametrize("pmax", [1, 4, 8, 12])
    def test_various_pmax(self, pmax):
        """Test various maximum lag settings."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        
        result = qadf(y, tau=0.5, pmax=pmax, verbose=False)
        assert result.lags <= pmax
    
    @pytest.mark.parametrize("ic", ['aic', 'bic', 't-stat'])
    def test_various_ic(self, ic):
        """Test various information criteria."""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(200))
        
        result = qadf(y, tau=0.5, ic=ic, verbose=False)
        assert isinstance(result, QADFResult)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
