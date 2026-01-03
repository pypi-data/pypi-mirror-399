"""
QADF - Quantile Autoregressive Distributed Lag Unit Root Test
==============================================================

A Python implementation of the Quantile Unit Root Test based on:

    Koenker, R., Xiao, Z. (2004). Unit Root Quantile Autoregression Inference.
    Journal of the American Statistical Association, 99, 775-787.
    DOI: 10.1198/016214504000001114

This package provides:
    - qadf(): Perform the QADF test at a single quantile
    - qadf_process(): Perform the QADF test across multiple quantiles
    - Bootstrap inference and critical value simulation
    - Publication-ready visualization tools

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantileadf

Installation
------------
    pip install qadf

Quick Start
-----------
    >>> import numpy as np
    >>> from qadf import qadf, qadf_process
    >>> 
    >>> # Generate random walk
    >>> np.random.seed(42)
    >>> y = np.cumsum(np.random.randn(200))
    >>> 
    >>> # Single quantile test
    >>> result = qadf(y, tau=0.5, model='c')
    >>> 
    >>> # Multiple quantiles
    >>> process_result = qadf_process(y)
    >>> df = process_result.to_dataframe()

License
-------
MIT License

Copyright (c) 2024 Dr Merwan Roudane
"""

__version__ = '1.0.0'
__author__ = 'Dr Merwan Roudane'
__email__ = 'merwanroudane920@gmail.com'
__url__ = 'https://github.com/merwanroudane/quantileadf'

# Core functions
from .core import (
    qadf,
    qadf_process,
    qr_adf,
    quantileADF,
    QRADF,
    QADFResult,
    QADFProcessResult,
    bandwidth_hs,
    bandwidth_bofinger,
)

# Bootstrap functions
from .bootstrap import (
    bootstrap_critical_values,
    bootstrap_pvalue,
    bootstrap_qadf_process,
    generate_bootstrap_sample,
    simulate_critical_values,
    BootstrapResult,
)

# Critical values
from .critical_values import (
    get_hansen_critical_values,
    get_critical_values_table,
    print_critical_values_table,
    get_asymptotic_critical_values_appendix,
    interpolate_critical_value,
    CriticalValueTable,
    HANSEN_CV_C,
    HANSEN_CV_CT,
    HANSEN_CV_NC,
)

# Visualization (optional import)
try:
    from .visualization import (
        plot_qadf_process,
        plot_qadf_comparison,
        plot_bootstrap_distribution,
        plot_coefficient_dynamics,
        create_summary_table,
    )
except ImportError:
    pass  # Matplotlib not installed

# All public exports
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    '__url__',
    
    # Core functions
    'qadf',
    'qadf_process',
    'qr_adf',
    'quantileADF',
    'QRADF',
    'QADFResult',
    'QADFProcessResult',
    'bandwidth_hs',
    'bandwidth_bofinger',
    
    # Bootstrap
    'bootstrap_critical_values',
    'bootstrap_pvalue',
    'bootstrap_qadf_process',
    'generate_bootstrap_sample',
    'simulate_critical_values',
    'BootstrapResult',
    
    # Critical values
    'get_hansen_critical_values',
    'get_critical_values_table',
    'print_critical_values_table',
    'get_asymptotic_critical_values_appendix',
    'interpolate_critical_value',
    'CriticalValueTable',
    'HANSEN_CV_C',
    'HANSEN_CV_CT',
    'HANSEN_CV_NC',
    
    # Visualization
    'plot_qadf_process',
    'plot_qadf_comparison',
    'plot_bootstrap_distribution',
    'plot_coefficient_dynamics',
    'create_summary_table',
]


def show_info():
    """Display package information."""
    info = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    QADF - Quantile ADF Unit Root Test                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Version:  {__version__:<66} ║
║  Author:   {__author__:<66} ║
║  Email:    {__email__:<66} ║
║  GitHub:   {__url__:<66} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Reference:                                                                   ║
║  Koenker, R., Xiao, Z. (2004). Unit Root Quantile Autoregression Inference.  ║
║  Journal of the American Statistical Association, 99, 775-787.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(info)


def cite():
    """Return citation for the methodology."""
    citation = """
@article{koenker2004unit,
  title={Unit Root Quantile Autoregression Inference},
  author={Koenker, Roger and Xiao, Zhijie},
  journal={Journal of the American Statistical Association},
  volume={99},
  number={467},
  pages={775--787},
  year={2004},
  publisher={Taylor \\& Francis},
  doi={10.1198/016214504000001114}
}

@software{qadf2024,
  title={QADF: Quantile ADF Unit Root Test for Python},
  author={Roudane, Merwan},
  year={2024},
  url={https://github.com/merwanroudane/quantileadf}
}
    """
    print(citation)
    return citation
