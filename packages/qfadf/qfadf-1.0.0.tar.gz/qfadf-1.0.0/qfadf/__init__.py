"""
QFADF - Quantile Fourier ADF Unit Root Test

A Python implementation of the Quantile Fourier ADF unit root test
proposed by Li & Zheng (2018).

Reference:
    Li, H., & Zheng, C. (2018).
    Unit root quantile autoregression testing with smooth structural changes.
    Finance Research Letters, 25, 83-89.

This package provides:
- qr_fourier_adf: Main test function for single quantile
- qr_fourier_adf_bootstrap: Bootstrap procedure for critical values
- qks_qcm_statistics: QKS and QCM tests over range of quantiles
- estimate_optimal_k: Optimal Fourier frequency selection
- Critical value functions and tables

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantilefourierunitroot

Example
-------
>>> import numpy as np
>>> from qfadf import qr_fourier_adf, qr_fourier_adf_bootstrap
>>> 
>>> # Generate a random walk (unit root process)
>>> np.random.seed(42)
>>> y = np.cumsum(np.random.randn(200))
>>> 
>>> # Basic test at median
>>> results = qr_fourier_adf(y, model=1, tau=0.5)
>>> 
>>> # Bootstrap for critical values
>>> boot_results = qr_fourier_adf_bootstrap(y, model=1, tau=0.5, n_boot=500)
"""

__version__ = "1.0.0"
__author__ = "Dr Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"
__license__ = "MIT"

from .core import (
    qr_fourier_adf,
    qks_qcm_statistics,
    estimate_optimal_k
)

from .bootstrap import (
    qr_fourier_adf_bootstrap,
    simulate_critical_values,
    generate_critical_value_tables
)

from .critical_values import (
    get_critical_values,
    interpolate_critical_value,
    print_critical_value_table,
    get_critical_value_dataframe,
    CRITICAL_VALUES_MODEL1,
    CRITICAL_VALUES_MODEL2
)

from .utils import (
    prepare_data,
    adf_lag_selection,
    summary_statistics,
    format_results_latex,
    format_results_dataframe,
    multiple_quantile_results_table,
    plot_quantile_results,
    export_results_csv,
    jarque_bera_test,
    ljung_box_test
)

__all__ = [
    # Core functions
    'qr_fourier_adf',
    'qks_qcm_statistics',
    'estimate_optimal_k',
    
    # Bootstrap functions
    'qr_fourier_adf_bootstrap',
    'simulate_critical_values',
    'generate_critical_value_tables',
    
    # Critical values
    'get_critical_values',
    'interpolate_critical_value',
    'print_critical_value_table',
    'get_critical_value_dataframe',
    'CRITICAL_VALUES_MODEL1',
    'CRITICAL_VALUES_MODEL2',
    
    # Utilities
    'prepare_data',
    'adf_lag_selection',
    'summary_statistics',
    'format_results_latex',
    'format_results_dataframe',
    'multiple_quantile_results_table',
    'plot_quantile_results',
    'export_results_csv',
    'jarque_bera_test',
    'ljung_box_test'
]
