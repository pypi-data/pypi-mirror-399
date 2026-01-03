"""
Utility Functions for Quantile Fourier ADF Test

This module provides utility functions for data preprocessing, diagnostics,
and result formatting.

Reference:
    Li, H., & Zheng, C. (2018).
    Unit root quantile autoregression testing with smooth structural changes.
    Finance Research Letters, 25, 83-89.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantilefourierunitroot
"""

import numpy as np
import pandas as pd
from typing import Union, Optional, Tuple, List, Dict
import warnings


def prepare_data(data: Union[np.ndarray, pd.Series, pd.DataFrame, list],
                 column: Optional[str] = None) -> np.ndarray:
    """
    Prepare input data for analysis.
    
    Parameters
    ----------
    data : array_like, Series, or DataFrame
        Input time series data.
    column : str, optional
        Column name if data is DataFrame.
        
    Returns
    -------
    y : np.ndarray
        Cleaned 1-dimensional numpy array.
    """
    if isinstance(data, pd.DataFrame):
        if column is not None:
            data = data[column]
        else:
            if data.shape[1] == 1:
                data = data.iloc[:, 0]
            else:
                raise ValueError("DataFrame has multiple columns. Specify 'column' parameter.")
    
    if isinstance(data, pd.Series):
        data = data.values
    
    if isinstance(data, list):
        data = np.array(data)
    
    data = np.asarray(data, dtype=np.float64).flatten()
    
    # Check for missing values
    if np.any(np.isnan(data)):
        warnings.warn("Data contains NaN values. Removing them.")
        data = data[~np.isnan(data)]
    
    # Check for infinite values
    if np.any(np.isinf(data)):
        warnings.warn("Data contains infinite values. Removing them.")
        data = data[~np.isinf(data)]
    
    return data


def adf_lag_selection(y: np.ndarray, max_lags: int = 12, 
                      criterion: str = 'aic') -> int:
    """
    Select optimal lag length using information criteria.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data.
    max_lags : int, optional
        Maximum number of lags to consider. Default is 12.
    criterion : str, optional
        Information criterion: 'aic', 'bic', or 'hqic'. Default is 'aic'.
        
    Returns
    -------
    opt_lag : int
        Optimal number of lags.
    """
    n = len(y)
    dy = np.diff(y)
    y_lag = y[:-1]
    
    ic_values = np.full(max_lags + 1, np.inf)
    
    for p in range(max_lags + 1):
        try:
            # Trim for lags
            start_idx = p + 1
            y_trim = y[start_idx:]
            y_lag_trim = y_lag[p:]
            T = len(y_trim)
            
            if T < 10:
                continue
            
            # Construct design matrix
            X = np.column_stack([np.ones(T), y_lag_trim])
            
            if p > 0:
                dy_lags = np.zeros((T, p))
                for j in range(1, p + 1):
                    dy_lags[:, j-1] = dy[p - j:p - j + T]
                X = np.column_stack([X, dy_lags])
            
            # OLS regression
            beta = np.linalg.lstsq(X, y_trim, rcond=None)[0]
            residuals = y_trim - X @ beta
            
            # Calculate RSS and information criterion
            rss = np.sum(residuals ** 2)
            sigma2 = rss / T
            k = X.shape[1]  # Number of parameters
            
            if criterion == 'aic':
                ic = np.log(sigma2) + 2 * k / T
            elif criterion == 'bic':
                ic = np.log(sigma2) + k * np.log(T) / T
            elif criterion == 'hqic':
                ic = np.log(sigma2) + 2 * k * np.log(np.log(T)) / T
            else:
                raise ValueError("criterion must be 'aic', 'bic', or 'hqic'")
            
            ic_values[p] = ic
            
        except Exception:
            continue
    
    opt_lag = np.argmin(ic_values)
    return opt_lag


def summary_statistics(y: np.ndarray) -> Dict:
    """
    Calculate summary statistics for time series.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data.
        
    Returns
    -------
    stats : dict
        Dictionary with summary statistics.
    """
    n = len(y)
    dy = np.diff(y)
    
    stats = {
        'n': n,
        'mean': np.mean(y),
        'std': np.std(y, ddof=1),
        'min': np.min(y),
        'max': np.max(y),
        'skewness': _skewness(y),
        'kurtosis': _kurtosis(y),
        'first_diff_mean': np.mean(dy),
        'first_diff_std': np.std(dy, ddof=1),
        'acf_1': _autocorr(y, 1),
        'acf_5': _autocorr(y, 5),
        'acf_10': _autocorr(y, 10)
    }
    
    return stats


def _skewness(x: np.ndarray) -> float:
    """Calculate sample skewness."""
    n = len(x)
    m = np.mean(x)
    s = np.std(x, ddof=1)
    if s == 0:
        return 0.0
    return np.sum((x - m) ** 3) / ((n - 1) * s ** 3)


def _kurtosis(x: np.ndarray) -> float:
    """Calculate sample excess kurtosis."""
    n = len(x)
    m = np.mean(x)
    s = np.std(x, ddof=1)
    if s == 0:
        return 0.0
    return np.sum((x - m) ** 4) / ((n - 1) * s ** 4) - 3


def _autocorr(x: np.ndarray, lag: int) -> float:
    """Calculate autocorrelation at specified lag."""
    if lag >= len(x):
        return np.nan
    return np.corrcoef(x[lag:], x[:-lag])[0, 1]


def format_results_latex(results: Dict, caption: str = "Quantile Fourier ADF Test Results",
                         label: str = "tab:qfadf") -> str:
    """
    Format test results as LaTeX table.
    
    Parameters
    ----------
    results : dict
        Test results dictionary.
    caption : str, optional
        Table caption.
    label : str, optional
        LaTeX label.
        
    Returns
    -------
    latex : str
        LaTeX formatted table.
    """
    model_name = "Constant" if results['model'] == 1 else "Constant + Trend"
    
    latex = [
        r"\begin{table}[htbp]",
        r"\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        r"\begin{tabular}{lc}",
        r"\toprule",
        r"Specification & Value \\",
        r"\midrule",
        f"Model & {model_name} \\\\",
        f"Fourier frequency ($k$) & {results['k']} \\\\",
        f"Lags ($p$) & {results['pmax']} \\\\",
        f"Sample size ($n$) & {results['n']} \\\\",
        r"\midrule",
        f"Quantile ($\\tau$) & {results['tau']:.3f} \\\\",
        f"$\\rho(\\tau)$ & {results['rho_tau']:.6f} \\\\",
        f"$t_f(\\tau)$ & {results['tn']:.4f} \\\\",
    ]
    
    if 'cv' in results:
        latex.extend([
            r"\midrule",
            r"Critical Values & \\",
            f"1\\% & {results['cv']['1%']:.4f} \\\\",
            f"5\\% & {results['cv']['5%']:.4f} \\\\",
            f"10\\% & {results['cv']['10%']:.4f} \\\\",
        ])
    
    if 'p_value' in results:
        latex.append(f"Bootstrap $p$-value & {results['p_value']:.4f} \\\\")
    
    latex.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{tablenotes}",
        r"\small",
        r"\item Notes: Based on Li \& Zheng (2018). $H_0$: Unit root ($\phi = 1$).",
        r"\end{tablenotes}",
        r"\end{table}"
    ])
    
    return "\n".join(latex)


def format_results_dataframe(results: Dict) -> pd.DataFrame:
    """
    Format test results as pandas DataFrame.
    
    Parameters
    ----------
    results : dict
        Test results dictionary.
        
    Returns
    -------
    df : pd.DataFrame
        Formatted results.
    """
    rows = []
    
    model_name = "Constant" if results['model'] == 1 else "Constant + Trend"
    
    rows.append({'Statistic': 'Model', 'Value': model_name})
    rows.append({'Statistic': 'Fourier frequency (k)', 'Value': str(results['k'])})
    rows.append({'Statistic': 'Lags (pmax)', 'Value': str(results['pmax'])})
    rows.append({'Statistic': 'Sample size (n)', 'Value': str(results['n'])})
    rows.append({'Statistic': 'Quantile (τ)', 'Value': f"{results['tau']:.3f}"})
    rows.append({'Statistic': 'ρ(τ)', 'Value': f"{results['rho_tau']:.6f}"})
    rows.append({'Statistic': 't_f(τ)', 'Value': f"{results['tn']:.4f}"})
    
    if 'cv' in results:
        rows.append({'Statistic': 'CV 1%', 'Value': f"{results['cv']['1%']:.4f}"})
        rows.append({'Statistic': 'CV 5%', 'Value': f"{results['cv']['5%']:.4f}"})
        rows.append({'Statistic': 'CV 10%', 'Value': f"{results['cv']['10%']:.4f}"})
    
    if 'p_value' in results:
        rows.append({'Statistic': 'Bootstrap p-value', 'Value': f"{results['p_value']:.4f}"})
    
    df = pd.DataFrame(rows)
    return df


def multiple_quantile_results_table(results_list: List[Dict]) -> pd.DataFrame:
    """
    Create comparison table for multiple quantile results.
    
    Parameters
    ----------
    results_list : list
        List of test results dictionaries for different quantiles.
        
    Returns
    -------
    df : pd.DataFrame
        Comparison table.
    """
    rows = []
    
    for r in results_list:
        row = {
            'τ': r['tau'],
            'ρ(τ)': r['rho_tau'],
            't_f(τ)': r['tn']
        }
        
        if 'cv' in r:
            row['CV 1%'] = r['cv']['1%']
            row['CV 5%'] = r['cv']['5%']
            row['CV 10%'] = r['cv']['10%']
        
        if 'p_value' in r:
            row['p-value'] = r['p_value']
        
        if 'reject_5pct' in r:
            row['Reject H0 (5%)'] = 'Yes' if r['reject_5pct'] else 'No'
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df


def plot_quantile_results(results_list: List[Dict], 
                          figsize: Tuple[int, int] = (12, 8),
                          save_path: Optional[str] = None):
    """
    Plot test statistics across quantiles.
    
    Parameters
    ----------
    results_list : list
        List of test results for different quantiles.
    figsize : tuple, optional
        Figure size. Default is (12, 8).
    save_path : str, optional
        Path to save figure.
        
    Returns
    -------
    fig, axes : matplotlib figure and axes
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
    
    taus = [r['tau'] for r in results_list]
    tn_values = [r['tn'] for r in results_list]
    rho_values = [r['rho_tau'] for r in results_list]
    
    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # Plot t_f(τ) statistics
    axes[0].plot(taus, tn_values, 'b-o', linewidth=2, markersize=8)
    axes[0].axhline(y=0, color='k', linestyle='--', alpha=0.5)
    axes[0].set_ylabel(r'$t_f(\tau)$', fontsize=12)
    axes[0].set_title('Quantile Fourier ADF Test Statistics', fontsize=14)
    axes[0].grid(True, alpha=0.3)
    
    # Add critical values if available
    if 'cv' in results_list[0]:
        cv_5 = [r['cv']['5%'] for r in results_list]
        axes[0].plot(taus, cv_5, 'r--', linewidth=1.5, label='5% CV')
        axes[0].legend()
    
    # Plot ρ(τ)
    axes[1].plot(taus, rho_values, 'g-o', linewidth=2, markersize=8)
    axes[1].axhline(y=1, color='k', linestyle='--', alpha=0.5, label=r'$\phi = 1$')
    axes[1].set_xlabel(r'Quantile $\tau$', fontsize=12)
    axes[1].set_ylabel(r'$\rho(\tau)$', fontsize=12)
    axes[1].set_title(r'Quantile Autoregressive Coefficient $\rho(\tau)$', fontsize=14)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig, axes


def export_results_csv(results: Dict, filename: str) -> None:
    """
    Export test results to CSV file.
    
    Parameters
    ----------
    results : dict
        Test results dictionary.
    filename : str
        Output filename.
    """
    df = format_results_dataframe(results)
    df.to_csv(filename, index=False)


def jarque_bera_test(y: np.ndarray) -> Dict:
    """
    Perform Jarque-Bera test for normality.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data.
        
    Returns
    -------
    results : dict
        Test statistic and p-value.
    """
    from scipy import stats
    
    n = len(y)
    s = _skewness(y)
    k = _kurtosis(y)
    
    jb = (n / 6) * (s**2 + (k**2) / 4)
    p_value = 1 - stats.chi2.cdf(jb, 2)
    
    return {
        'statistic': jb,
        'p_value': p_value,
        'skewness': s,
        'kurtosis': k
    }


def ljung_box_test(y: np.ndarray, lags: int = 10) -> Dict:
    """
    Perform Ljung-Box test for serial correlation.
    
    Parameters
    ----------
    y : np.ndarray
        Time series data (typically residuals).
    lags : int, optional
        Number of lags. Default is 10.
        
    Returns
    -------
    results : dict
        Test statistic and p-value.
    """
    from scipy import stats
    
    n = len(y)
    acf_values = np.array([_autocorr(y, k) for k in range(1, lags + 1)])
    
    q = n * (n + 2) * np.sum(acf_values**2 / (n - np.arange(1, lags + 1)))
    p_value = 1 - stats.chi2.cdf(q, lags)
    
    return {
        'statistic': q,
        'p_value': p_value,
        'lags': lags
    }
