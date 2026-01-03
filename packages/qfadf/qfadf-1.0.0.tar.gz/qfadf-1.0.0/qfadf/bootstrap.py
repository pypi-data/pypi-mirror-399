"""
Bootstrap Procedures for Quantile Fourier ADF Test

This module implements the bootstrap procedure for computing critical values
as described in Li & Zheng (2018) Section 3.2.

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
from typing import Union, Optional, Tuple, Dict, List
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

from .core import (_check_data, _get_fourier_terms, _get_deterministic_components,
                   _quantile_regression, _estimate_sparsity, _compute_tn_statistic,
                   qr_fourier_adf, qks_qcm_statistics)


def _generate_bootstrap_sample(y: np.ndarray, model: int, k: int, pmax: int) -> np.ndarray:
    """
    Generate a single bootstrap sample under the null hypothesis of unit root.
    
    Following Li & Zheng (2018) Section 3.2 (p.86):
    1. Calculate y_t^d = y_t - β̂'x_t (detrend using OLS)
    2. Estimate AR(1): y_t^d = φ̂ y_{t-1}^d + μ_t
    3. Resample with replacement from centered residuals
    4. Build bootstrap sample recursively under unit root null
    
    Parameters
    ----------
    y : np.ndarray
        Original time series.
    model : int
        Model specification (1 or 2).
    k : int
        Fourier frequency.
    pmax : int
        Number of lags.
        
    Returns
    -------
    y_star : np.ndarray
        Bootstrap sample under H0.
    """
    T = len(y)
    
    # Step (i): Construct x_t and detrend
    # x_t = (1, sin(2πkt/T), cos(2πkt/T), t) for model 2
    # x_t = (1, sin(2πkt/T), cos(2πkt/T)) for model 1
    
    constant = np.ones(T)
    sin_k, cos_k = _get_fourier_terms(T, k)
    
    if model == 1:
        X = np.column_stack([constant, sin_k, cos_k])
    else:  # model == 2
        trend = np.arange(1, T + 1)
        X = np.column_stack([constant, trend, sin_k, cos_k])
    
    # Add lagged differences to X if pmax > 0
    dy = np.diff(y)
    if pmax > 0:
        dy_lags = np.zeros((T, pmax))
        for j in range(1, pmax + 1):
            dy_padded = np.concatenate([np.zeros(j), dy[:T-j]])
            dy_lags[:, j-1] = dy_padded
        X = np.hstack([X, dy_lags])
    
    # Trim for lags
    X = X[pmax+1:]
    y_trim = y[pmax+1:]
    
    # OLS regression to detrend
    try:
        beta_ols = np.linalg.lstsq(X, y_trim, rcond=None)[0]
        y_d = y_trim - X @ beta_ols
    except np.linalg.LinAlgError:
        y_d = y_trim - np.mean(y_trim)
    
    # Step (ii): Estimate AR(1) from detrended series
    y_d_lag = y_d[:-1]
    y_d_current = y_d[1:]
    
    try:
        phi_hat = np.dot(y_d_lag, y_d_current) / np.dot(y_d_lag, y_d_lag)
    except (ZeroDivisionError, FloatingPointError):
        phi_hat = 0.0
    
    # Calculate residuals
    mu = y_d_current - phi_hat * y_d_lag
    
    # Center residuals
    mu_centered = mu - np.mean(mu)
    
    # Step (iii): Resample with replacement
    tt = len(mu_centered)
    indices = np.random.randint(0, tt, size=tt)
    mu_star = mu_centered[indices]
    
    # Step (iv): Build bootstrap sample under unit root null (φ = 1)
    y_d_star = np.zeros(tt)
    y_d_star[0] = mu_star[0]
    for s in range(1, tt):
        y_d_star[s] = y_d_star[s-1] + mu_star[s]
    
    # The bootstrap sample is the demeaned unit root process
    y_star = y_d_star
    
    return y_star


def _single_bootstrap_iteration(args: Tuple) -> Tuple[float, float, float]:
    """
    Perform a single bootstrap iteration.
    
    Parameters
    ----------
    args : tuple
        (y, model, tau, pmax, k, tau_range, compute_qks_qcm)
        
    Returns
    -------
    tuple
        (tn_boot, qks_boot, qcm_boot) - bootstrap test statistics
    """
    y, model, tau, pmax, k, tau_range, compute_qks_qcm = args
    
    # Generate bootstrap sample
    y_star = _generate_bootstrap_sample(y, model, k, pmax)
    
    # Compute bootstrap test statistic
    try:
        result = qr_fourier_adf(y_star, model=model, tau=tau, pmax=pmax, k=k, 
                                print_results=False)
        tn_boot = result['tn']
    except Exception:
        tn_boot = np.nan
    
    qks_boot = np.nan
    qcm_boot = np.nan
    
    if compute_qks_qcm:
        try:
            qks_qcm_result = qks_qcm_statistics(y_star, model=model, pmax=pmax, k=k,
                                                 tau_range=tau_range, n_quantiles=9)
            qks_boot = qks_qcm_result['QKS_f']
            qcm_boot = qks_qcm_result['QCM_f']
        except Exception:
            pass
    
    return tn_boot, qks_boot, qcm_boot


def qr_fourier_adf_bootstrap(y: Union[np.ndarray, pd.Series],
                              model: int = 1,
                              tau: float = 0.5,
                              pmax: int = 8,
                              k: int = 3,
                              n_boot: int = 1000,
                              compute_qks_qcm: bool = False,
                              tau_range: Tuple[float, float] = (0.1, 0.9),
                              n_jobs: int = 1,
                              random_state: Optional[int] = None,
                              print_results: bool = True) -> Dict:
    """
    Bootstrap procedure for Quantile Fourier ADF test critical values.
    
    This implements the bootstrap procedure from Li & Zheng (2018) Section 3.2
    to obtain finite-sample critical values.
    
    Parameters
    ----------
    y : array_like
        Time series data.
    model : int, optional
        Model specification: 1 (constant) or 2 (constant + trend). Default is 1.
    tau : float, optional
        Quantile level (0 < tau < 1). Default is 0.5.
    pmax : int, optional
        Number of lags. Default is 8.
    k : int, optional
        Fourier frequency (1-5). Default is 3.
    n_boot : int, optional
        Number of bootstrap replications. Default is 1000.
    compute_qks_qcm : bool, optional
        If True, also compute bootstrap critical values for QKS_f and QCM_f.
        Default is False.
    tau_range : tuple, optional
        Range of quantiles for QKS/QCM. Default is (0.1, 0.9).
    n_jobs : int, optional
        Number of parallel jobs. Default is 1 (sequential).
    random_state : int, optional
        Random seed for reproducibility.
    print_results : bool, optional
        If True, print formatted results. Default is True.
        
    Returns
    -------
    results : dict
        Dictionary containing:
        - 'tn': Original test statistic
        - 'tn_boot': Array of bootstrap test statistics
        - 'cv': Critical values at 1%, 5%, 10% significance levels
        - 'p_value': Bootstrap p-value
        - 'reject_1pct': Boolean, reject at 1% level
        - 'reject_5pct': Boolean, reject at 5% level
        - 'reject_10pct': Boolean, reject at 10% level
        
        If compute_qks_qcm=True, also includes:
        - 'QKS_f': Original QKS statistic
        - 'QCM_f': Original QCM statistic
        - 'cv_qks': Critical values for QKS_f
        - 'cv_qcm': Critical values for QCM_f
        
    References
    ----------
    Li, H., & Zheng, C. (2018). Unit root quantile autoregression testing with
    smooth structural changes. Finance Research Letters, 25, 83-89.
    
    Examples
    --------
    >>> import numpy as np
    >>> from qfadf import qr_fourier_adf_bootstrap
    >>> np.random.seed(42)
    >>> y = np.cumsum(np.random.randn(200))
    >>> results = qr_fourier_adf_bootstrap(y, model=1, tau=0.5, n_boot=500)
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Validate inputs
    y = _check_data(y)
    
    if not 0 < tau < 1:
        raise ValueError("tau must be between 0 and 1 (exclusive)")
    
    if model not in [1, 2]:
        raise ValueError("model must be 1 or 2")
    
    if n_boot < 100:
        warnings.warn("n_boot < 100 may lead to unreliable critical values")
    
    # Compute original test statistic
    original_result = qr_fourier_adf(y, model=model, tau=tau, pmax=pmax, k=k, 
                                     print_results=False)
    tn_original = original_result['tn']
    
    # Compute original QKS and QCM if requested
    qks_original = np.nan
    qcm_original = np.nan
    if compute_qks_qcm:
        qks_qcm_result = qks_qcm_statistics(y, model=model, pmax=pmax, k=k,
                                            tau_range=tau_range)
        qks_original = qks_qcm_result['QKS_f']
        qcm_original = qks_qcm_result['QCM_f']
    
    # Bootstrap iterations
    tn_boot = np.zeros(n_boot)
    qks_boot = np.zeros(n_boot) if compute_qks_qcm else None
    qcm_boot = np.zeros(n_boot) if compute_qks_qcm else None
    
    if n_jobs == 1:
        # Sequential execution
        for b in range(n_boot):
            y_star = _generate_bootstrap_sample(y, model, k, pmax)
            
            try:
                result = qr_fourier_adf(y_star, model=model, tau=tau, pmax=pmax, k=k,
                                        print_results=False)
                tn_boot[b] = result['tn']
            except Exception:
                tn_boot[b] = np.nan
            
            if compute_qks_qcm:
                try:
                    qks_qcm_b = qks_qcm_statistics(y_star, model=model, pmax=pmax, k=k,
                                                   tau_range=tau_range, n_quantiles=9)
                    qks_boot[b] = qks_qcm_b['QKS_f']
                    qcm_boot[b] = qks_qcm_b['QCM_f']
                except Exception:
                    qks_boot[b] = np.nan
                    qcm_boot[b] = np.nan
    else:
        # Parallel execution
        args_list = [(y, model, tau, pmax, k, tau_range, compute_qks_qcm) 
                     for _ in range(n_boot)]
        
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            results_list = list(executor.map(_single_bootstrap_iteration, args_list))
        
        for b, (tn_b, qks_b, qcm_b) in enumerate(results_list):
            tn_boot[b] = tn_b
            if compute_qks_qcm:
                qks_boot[b] = qks_b
                qcm_boot[b] = qcm_b
    
    # Remove NaN values
    tn_boot_valid = tn_boot[~np.isnan(tn_boot)]
    
    if len(tn_boot_valid) < n_boot * 0.9:
        warnings.warn(f"Many bootstrap iterations failed ({n_boot - len(tn_boot_valid)} out of {n_boot})")
    
    # Sort bootstrap statistics
    tn_boot_sorted = np.sort(tn_boot_valid)
    n_valid = len(tn_boot_sorted)
    
    # Critical values at 1%, 5%, 10% levels
    # For left-tailed test: cv is the α-th percentile
    cv_1pct = tn_boot_sorted[int(0.01 * n_valid)] if n_valid > 0 else np.nan
    cv_5pct = tn_boot_sorted[int(0.05 * n_valid)] if n_valid > 0 else np.nan
    cv_10pct = tn_boot_sorted[int(0.10 * n_valid)] if n_valid > 0 else np.nan
    
    # Bootstrap p-value (proportion of bootstrap statistics less than original)
    p_value = np.mean(tn_boot_valid <= tn_original)
    
    # Prepare results
    results = {
        'tn': tn_original,
        'rho_tau': original_result['rho_tau'],
        'tau': tau,
        'model': model,
        'k': k,
        'pmax': pmax,
        'n': original_result['n'],
        'n_boot': n_boot,
        'tn_boot': tn_boot,
        'cv': {'1%': cv_1pct, '5%': cv_5pct, '10%': cv_10pct},
        'p_value': p_value,
        'reject_1pct': tn_original < cv_1pct,
        'reject_5pct': tn_original < cv_5pct,
        'reject_10pct': tn_original < cv_10pct
    }
    
    # QKS and QCM critical values
    if compute_qks_qcm:
        qks_boot_valid = qks_boot[~np.isnan(qks_boot)]
        qcm_boot_valid = qcm_boot[~np.isnan(qcm_boot)]
        
        qks_boot_sorted = np.sort(qks_boot_valid)
        qcm_boot_sorted = np.sort(qcm_boot_valid)
        
        n_qks = len(qks_boot_sorted)
        n_qcm = len(qcm_boot_sorted)
        
        # For sup-type test, critical value is at (1-α) percentile
        results['QKS_f'] = qks_original
        results['cv_qks'] = {
            '1%': qks_boot_sorted[int(0.99 * n_qks)] if n_qks > 0 else np.nan,
            '5%': qks_boot_sorted[int(0.95 * n_qks)] if n_qks > 0 else np.nan,
            '10%': qks_boot_sorted[int(0.90 * n_qks)] if n_qks > 0 else np.nan
        }
        
        results['QCM_f'] = qcm_original
        results['cv_qcm'] = {
            '1%': qcm_boot_sorted[int(0.99 * n_qcm)] if n_qcm > 0 else np.nan,
            '5%': qcm_boot_sorted[int(0.95 * n_qcm)] if n_qcm > 0 else np.nan,
            '10%': qcm_boot_sorted[int(0.90 * n_qcm)] if n_qcm > 0 else np.nan
        }
    
    if print_results:
        _print_bootstrap_results(results, compute_qks_qcm)
    
    return results


def _print_bootstrap_results(results: Dict, include_qks_qcm: bool = False) -> None:
    """
    Print formatted bootstrap test results.
    
    Parameters
    ----------
    results : dict
        Bootstrap test results.
    include_qks_qcm : bool
        Whether to include QKS and QCM results.
    """
    model_desc = "Constant" if results['model'] == 1 else "Constant + Trend"
    
    print("\n" + "=" * 75)
    print("           QUANTILE FOURIER ADF UNIT ROOT TEST - BOOTSTRAP")
    print("           Li & Zheng (2018, Finance Research Letters)")
    print("=" * 75)
    print(f"\n  Model:                 {model_desc}")
    print(f"  Fourier frequency k:   {results['k']}")
    print(f"  Lags (pmax):           {results['pmax']}")
    print(f"  Sample size:           {results['n']}")
    print(f"  Bootstrap replications: {results['n_boot']}")
    
    print("\n" + "-" * 75)
    print("  t_f(τ) Test Results:")
    print("-" * 75)
    print(f"  Quantile (τ):          {results['tau']:.3f}")
    print(f"  ρ(τ):                  {results['rho_tau']:.6f}")
    print(f"  t_f(τ) statistic:      {results['tn']:.4f}")
    print(f"  Bootstrap p-value:     {results['p_value']:.4f}")
    
    print("\n  Bootstrap Critical Values:")
    print(f"    1% level:            {results['cv']['1%']:.4f}")
    print(f"    5% level:            {results['cv']['5%']:.4f}")
    print(f"    10% level:           {results['cv']['10%']:.4f}")
    
    print("\n  Decision:")
    if results['reject_1pct']:
        print("    *** Reject H0 at 1% significance level ***")
    elif results['reject_5pct']:
        print("    **  Reject H0 at 5% significance level **")
    elif results['reject_10pct']:
        print("    *   Reject H0 at 10% significance level *")
    else:
        print("        Fail to reject H0 (unit root)")
    
    if include_qks_qcm and 'QKS_f' in results:
        print("\n" + "-" * 75)
        print("  QKS_f and QCM_f Test Results:")
        print("-" * 75)
        print(f"  QKS_f statistic:       {results['QKS_f']:.4f}")
        print("  QKS_f Critical Values:")
        print(f"    1% level:            {results['cv_qks']['1%']:.4f}")
        print(f"    5% level:            {results['cv_qks']['5%']:.4f}")
        print(f"    10% level:           {results['cv_qks']['10%']:.4f}")
        
        print(f"\n  QCM_f statistic:       {results['QCM_f']:.4f}")
        print("  QCM_f Critical Values:")
        print(f"    1% level:            {results['cv_qcm']['1%']:.4f}")
        print(f"    5% level:            {results['cv_qcm']['5%']:.4f}")
        print(f"    10% level:           {results['cv_qcm']['10%']:.4f}")
    
    print("\n" + "-" * 75)
    print("  H0: Unit root (φ = 1)")
    print("  H1: Stationary (φ < 1)")
    print("  Reject H0 if t_f(τ) < critical value (left-tailed test)")
    print("=" * 75 + "\n")


def simulate_critical_values(n_obs: int,
                             model: int = 1,
                             tau: float = 0.5,
                             pmax: int = 8,
                             k: int = 3,
                             n_simulations: int = 10000,
                             random_state: Optional[int] = None) -> Dict:
    """
    Simulate critical values through Monte Carlo simulation.
    
    This function generates critical values by simulating unit root processes
    and computing the test statistic distribution.
    
    Parameters
    ----------
    n_obs : int
        Sample size for simulation.
    model : int, optional
        Model specification (1 or 2). Default is 1.
    tau : float, optional
        Quantile level. Default is 0.5.
    pmax : int, optional
        Number of lags. Default is 8.
    k : int, optional
        Fourier frequency. Default is 3.
    n_simulations : int, optional
        Number of Monte Carlo simulations. Default is 10000.
    random_state : int, optional
        Random seed for reproducibility.
        
    Returns
    -------
    results : dict
        Dictionary containing:
        - 'cv': Critical values at various significance levels
        - 'statistics': Array of simulated test statistics
        - 'percentiles': Various percentiles of the distribution
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    statistics = np.zeros(n_simulations)
    
    for i in range(n_simulations):
        # Generate unit root process: y_t = y_{t-1} + μ_t
        mu = np.random.randn(n_obs)
        y = np.cumsum(mu)
        
        try:
            result = qr_fourier_adf(y, model=model, tau=tau, pmax=pmax, k=k,
                                    print_results=False)
            statistics[i] = result['tn']
        except Exception:
            statistics[i] = np.nan
    
    # Remove NaN values
    valid_stats = statistics[~np.isnan(statistics)]
    sorted_stats = np.sort(valid_stats)
    n_valid = len(sorted_stats)
    
    # Critical values for left-tailed test
    cv = {
        '1%': sorted_stats[int(0.01 * n_valid)],
        '2.5%': sorted_stats[int(0.025 * n_valid)],
        '5%': sorted_stats[int(0.05 * n_valid)],
        '10%': sorted_stats[int(0.10 * n_valid)]
    }
    
    # Various percentiles
    percentiles = {}
    for p in [1, 2.5, 5, 10, 25, 50, 75, 90, 95, 97.5, 99]:
        percentiles[f'{p}%'] = np.percentile(valid_stats, p)
    
    results = {
        'n_obs': n_obs,
        'model': model,
        'tau': tau,
        'k': k,
        'pmax': pmax,
        'n_simulations': n_simulations,
        'cv': cv,
        'statistics': valid_stats,
        'percentiles': percentiles,
        'mean': np.mean(valid_stats),
        'std': np.std(valid_stats)
    }
    
    return results


def generate_critical_value_tables(sample_sizes: List[int] = [100, 200, 500, 1000],
                                   models: List[int] = [1, 2],
                                   tau_values: List[float] = [0.1, 0.25, 0.5, 0.75, 0.9],
                                   k_values: List[int] = [1, 2, 3, 4, 5],
                                   n_simulations: int = 10000,
                                   random_state: Optional[int] = None) -> pd.DataFrame:
    """
    Generate comprehensive critical value tables.
    
    Parameters
    ----------
    sample_sizes : list
        List of sample sizes to simulate.
    models : list
        List of models (1 and/or 2).
    tau_values : list
        List of quantile levels.
    k_values : list
        List of Fourier frequencies.
    n_simulations : int
        Number of simulations per configuration.
    random_state : int, optional
        Random seed.
        
    Returns
    -------
    cv_table : pd.DataFrame
        DataFrame with critical values for all configurations.
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    results_list = []
    
    total_combinations = len(sample_sizes) * len(models) * len(tau_values) * len(k_values)
    current = 0
    
    for n in sample_sizes:
        for model in models:
            for tau in tau_values:
                for k in k_values:
                    current += 1
                    print(f"Simulating {current}/{total_combinations}: n={n}, model={model}, tau={tau}, k={k}")
                    
                    try:
                        result = simulate_critical_values(
                            n_obs=n, model=model, tau=tau, k=k,
                            n_simulations=n_simulations
                        )
                        
                        results_list.append({
                            'n': n,
                            'model': model,
                            'tau': tau,
                            'k': k,
                            'cv_1pct': result['cv']['1%'],
                            'cv_5pct': result['cv']['5%'],
                            'cv_10pct': result['cv']['10%'],
                            'mean': result['mean'],
                            'std': result['std']
                        })
                    except Exception as e:
                        warnings.warn(f"Error at n={n}, model={model}, tau={tau}, k={k}: {str(e)}")
    
    cv_table = pd.DataFrame(results_list)
    return cv_table
