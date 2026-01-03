"""
Visualization Functions for QADF Test
======================================

This module provides plotting functions for visualizing QADF test results,
including quantile process plots and coefficient dynamics.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantileadf
"""

import numpy as np
from typing import Optional, List, Tuple, Union
import warnings

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    warnings.warn("Matplotlib not available. Plotting functions will not work.")


def _check_matplotlib():
    """Check if matplotlib is available."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "Matplotlib is required for plotting. "
            "Install it with: pip install matplotlib"
        )


def plot_qadf_process(result, 
                      figsize: Tuple[int, int] = (12, 8),
                      include_ols: bool = True,
                      include_ci: bool = True,
                      alpha: float = 0.05,
                      title: Optional[str] = None,
                      save_path: Optional[str] = None) -> None:
    """
    Plot the quantile autoregressive process results.
    
    This creates a figure similar to those in Koenker & Xiao (2004),
    showing how the autoregressive coefficient varies across quantiles.
    
    Parameters
    ----------
    result : QADFProcessResult
        Result object from qadf_process().
    figsize : tuple
        Figure size (width, height).
    include_ols : bool
        Whether to include the OLS estimate as a reference line.
    include_ci : bool
        Whether to include confidence intervals (requires bootstrap).
    alpha : float
        Significance level for confidence intervals.
    title : str, optional
        Custom title for the plot.
    save_path : str, optional
        Path to save the figure.
    
    Returns
    -------
    None
        Displays the plot.
    """
    _check_matplotlib()
    
    quantiles = result.quantiles
    rho_tau = np.array([r.rho_tau for r in result.results])
    rho_ols = result.results[0].rho_ols  # Same for all quantiles
    t_stats = np.array([r.statistic for r in result.results])
    cv_5pct = np.array([r.critical_values['5%'] for r in result.results])
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Plot 1: ρ₁(τ) - Autoregressive coefficient
    ax1 = axes[0, 0]
    ax1.plot(quantiles, rho_tau, 'b-', linewidth=2, label='ρ₁(τ) [QR]')
    ax1.axhline(y=1, color='r', linestyle='--', linewidth=1.5, label='Unit Root (ρ=1)')
    if include_ols:
        ax1.axhline(y=rho_ols, color='g', linestyle=':', linewidth=1.5, label='ρ₁ [OLS]')
    ax1.set_xlabel('Quantile (τ)', fontsize=11)
    ax1.set_ylabel('ρ₁(τ)', fontsize=11)
    ax1.set_title('Autoregressive Coefficient', fontsize=12)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1])
    
    # Plot 2: t-statistic with critical values
    ax2 = axes[0, 1]
    ax2.plot(quantiles, t_stats, 'b-', linewidth=2, label='tₙ(τ)')
    ax2.plot(quantiles, cv_5pct, 'r--', linewidth=1.5, label='5% CV')
    ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax2.fill_between(quantiles, cv_5pct, np.min(t_stats) - 0.5, 
                     alpha=0.2, color='red', label='Rejection Region')
    ax2.set_xlabel('Quantile (τ)', fontsize=11)
    ax2.set_ylabel('tₙ(τ)', fontsize=11)
    ax2.set_title('QADF t-Statistic', fontsize=12)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1])
    
    # Plot 3: δ² across quantiles
    ax3 = axes[1, 0]
    delta2 = np.array([r.delta2 for r in result.results])
    ax3.plot(quantiles, delta2, 'b-', linewidth=2, marker='o', markersize=4)
    ax3.set_xlabel('Quantile (τ)', fontsize=11)
    ax3.set_ylabel('δ²', fontsize=11)
    ax3.set_title('Nuisance Parameter δ²', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 1])
    ax3.set_ylim([0, 1])
    
    # Plot 4: Half-lives
    ax4 = axes[1, 1]
    half_lives = []
    for r in result.results:
        if isinstance(r.half_life, str):
            half_lives.append(np.nan)
        else:
            half_lives.append(min(r.half_life, 100))  # Cap at 100 for visualization
    
    half_lives = np.array(half_lives)
    mask = ~np.isnan(half_lives)
    
    if np.any(mask):
        ax4.plot(quantiles[mask], half_lives[mask], 'b-', linewidth=2, marker='o', markersize=4)
        ax4.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax4.set_xlabel('Quantile (τ)', fontsize=11)
    ax4.set_ylabel('Half-life', fontsize=11)
    ax4.set_title('Shock Half-life (∞ shown as missing)', fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim([0, 1])
    
    # Overall title
    if title is None:
        title = 'Quantile ADF Unit Root Test Results'
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    plt.show()


def plot_qadf_comparison(results_list: List,
                         labels: List[str],
                         figsize: Tuple[int, int] = (14, 6),
                         title: Optional[str] = None,
                         save_path: Optional[str] = None) -> None:
    """
    Compare QADF results across multiple series.
    
    Parameters
    ----------
    results_list : List[QADFProcessResult]
        List of QADF process results.
    labels : List[str]
        Labels for each series.
    figsize : tuple
        Figure size.
    title : str, optional
        Custom title.
    save_path : str, optional
        Path to save figure.
    """
    _check_matplotlib()
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(results_list)))
    
    # Plot 1: ρ₁(τ) comparison
    ax1 = axes[0]
    for i, (result, label) in enumerate(zip(results_list, labels)):
        quantiles = result.quantiles
        rho_tau = np.array([r.rho_tau for r in result.results])
        ax1.plot(quantiles, rho_tau, color=colors[i], linewidth=2, label=label)
    
    ax1.axhline(y=1, color='black', linestyle='--', linewidth=1.5, label='Unit Root')
    ax1.set_xlabel('Quantile (τ)', fontsize=11)
    ax1.set_ylabel('ρ₁(τ)', fontsize=11)
    ax1.set_title('Autoregressive Coefficients', fontsize=12)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1])
    
    # Plot 2: t-statistic comparison
    ax2 = axes[1]
    for i, (result, label) in enumerate(zip(results_list, labels)):
        quantiles = result.quantiles
        t_stats = np.array([r.statistic for r in result.results])
        ax2.plot(quantiles, t_stats, color=colors[i], linewidth=2, label=label)
    
    # Use first result's CV as reference
    cv_5pct = np.array([r.critical_values['5%'] for r in results_list[0].results])
    ax2.plot(results_list[0].quantiles, cv_5pct, 'k--', linewidth=1.5, label='5% CV (approx)')
    ax2.set_xlabel('Quantile (τ)', fontsize=11)
    ax2.set_ylabel('tₙ(τ)', fontsize=11)
    ax2.set_title('QADF t-Statistics', fontsize=12)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1])
    
    if title is None:
        title = 'QADF Comparison Across Series'
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_bootstrap_distribution(boot_result,
                                figsize: Tuple[int, int] = (10, 6),
                                bins: int = 50,
                                title: Optional[str] = None,
                                save_path: Optional[str] = None) -> None:
    """
    Plot the bootstrap distribution of the test statistic.
    
    Parameters
    ----------
    boot_result : BootstrapResult
        Result from bootstrap_pvalue().
    figsize : tuple
        Figure size.
    bins : int
        Number of histogram bins.
    title : str, optional
        Custom title.
    save_path : str, optional
        Path to save figure.
    """
    _check_matplotlib()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Histogram of bootstrap distribution
    ax.hist(boot_result.bootstrap_distribution, bins=bins, density=True,
            alpha=0.7, color='steelblue', edgecolor='white', label='Bootstrap Distribution')
    
    # Vertical line for test statistic
    ax.axvline(x=boot_result.test_statistic, color='red', linestyle='-', 
               linewidth=2, label=f'Test Statistic: {boot_result.test_statistic:.4f}')
    
    # Critical values
    for level, color in [('1%', 'darkred'), ('5%', 'red'), ('10%', 'orange')]:
        cv = boot_result.critical_values[level]
        ax.axvline(x=cv, color=color, linestyle='--', linewidth=1.5,
                   label=f'{level} CV: {cv:.4f}')
    
    ax.set_xlabel('Test Statistic', fontsize=11)
    ax.set_ylabel('Density', fontsize=11)
    
    if title is None:
        title = f'Bootstrap Distribution (p-value: {boot_result.pvalue:.4f})'
    ax.set_title(title, fontsize=12)
    
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_coefficient_dynamics(result,
                              figsize: Tuple[int, int] = (10, 6),
                              include_bands: bool = True,
                              title: Optional[str] = None,
                              save_path: Optional[str] = None) -> None:
    """
    Create a publication-quality plot of coefficient dynamics.
    
    This creates a plot similar to Figure 1 in interest rate studies
    showing asymmetric persistence across quantiles.
    
    Parameters
    ----------
    result : QADFProcessResult
        QADF process result.
    figsize : tuple
        Figure size.
    include_bands : bool
        Whether to include shaded regions.
    title : str, optional
        Custom title.
    save_path : str, optional
        Path to save figure.
    """
    _check_matplotlib()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    quantiles = result.quantiles
    rho_tau = np.array([r.rho_tau for r in result.results])
    rho_ols = result.results[0].rho_ols
    
    # Main line for quantile estimates
    ax.plot(quantiles, rho_tau, 'b-', linewidth=2.5, label='ρ₁(τ) - Quantile Regression')
    
    # OLS estimate
    ax.axhline(y=rho_ols, color='green', linestyle='-.', linewidth=2, 
               label=f'ρ₁ - OLS: {rho_ols:.4f}')
    
    # Unit root line
    ax.axhline(y=1, color='red', linestyle='--', linewidth=2, label='Unit Root (ρ₁ = 1)')
    
    # Shaded regions
    if include_bands:
        ax.fill_between(quantiles, 0.8, rho_tau, where=rho_tau < 1,
                       alpha=0.2, color='blue', label='Stationary Region')
        ax.fill_between(quantiles, rho_tau, 1.2, where=rho_tau > 1,
                       alpha=0.2, color='red', label='Explosive Region')
    
    # Mark significant points
    for r in result.results:
        if r.statistic < r.critical_values['5%']:
            ax.plot(r.quantile, r.rho_tau, 'go', markersize=8)
    
    ax.set_xlabel('Quantile (τ)', fontsize=12)
    ax.set_ylabel('Autoregressive Coefficient ρ₁(τ)', fontsize=12)
    
    if title is None:
        title = 'Quantile Autoregressive Coefficient Dynamics'
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    ax.legend(loc='best', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([min(quantiles) - 0.05, max(quantiles) + 0.05])
    
    # Add annotation
    ax.annotate('Lower quantiles:\nMore stationary', 
                xy=(0.15, np.mean(rho_tau[:3])), fontsize=9,
                ha='center', va='bottom')
    ax.annotate('Upper quantiles:\nMore persistent', 
                xy=(0.85, np.mean(rho_tau[-3:])), fontsize=9,
                ha='center', va='top')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    plt.show()


def create_summary_table(result, format: str = 'latex') -> str:
    """
    Create a publication-ready summary table.
    
    Parameters
    ----------
    result : QADFProcessResult
        QADF process result.
    format : str
        Output format: 'latex', 'markdown', or 'text'.
    
    Returns
    -------
    str
        Formatted table string.
    """
    df = result.to_dataframe()
    
    if format == 'latex':
        # LaTeX table
        latex = df[['rho_tau', 'statistic', 'cv_5pct', 'delta2']].to_latex(
            float_format='%.4f',
            caption='Quantile ADF Unit Root Test Results',
            label='tab:qadf_results',
            column_format='c' * 5
        )
        
        # Rename columns for LaTeX
        latex = latex.replace('rho_tau', r'$\hat{\rho}_1(\tau)$')
        latex = latex.replace('statistic', r'$t_n(\tau)$')
        latex = latex.replace('cv_5pct', r'CV(5\%)')
        latex = latex.replace('delta2', r'$\hat{\delta}^2$')
        
        return latex
    
    elif format == 'markdown':
        # Markdown table
        lines = [
            "| Quantile | ρ₁(τ) | tₙ(τ) | CV(5%) | δ² |",
            "|----------|-------|-------|--------|-----|"
        ]
        
        for r in result.results:
            lines.append(
                f"| {r.quantile:.2f} | {r.rho_tau:.4f} | {r.statistic:.4f} | "
                f"{r.critical_values['5%']:.4f} | {r.delta2:.4f} |"
            )
        
        return '\n'.join(lines)
    
    else:
        # Plain text
        return str(result)
