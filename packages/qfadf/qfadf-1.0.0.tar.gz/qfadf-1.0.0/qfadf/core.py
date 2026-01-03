"""
Quantile Fourier ADF Unit Root Test

Reference:
    Li, H., & Zheng, C. (2018).
    Unit root quantile autoregression testing with smooth structural changes.
    Finance Research Letters, 25, 83-89.

This module implements the Quantile Fourier ADF unit root test which is robust
to both non-Gaussian conditions and structural changes.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/quantilefourierunitroot
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Union, Optional, Tuple, List, Dict
import warnings


def _check_data(y: np.ndarray) -> np.ndarray:
    """
    Check and prepare input data.
    
    Parameters
    ----------
    y : array_like
        Input time series data.
        
    Returns
    -------
    y : np.ndarray
        Validated and cleaned data array.
    """
    y = np.asarray(y, dtype=np.float64).flatten()
    
    if np.any(np.isnan(y)):
        raise ValueError("Input data contains missing values (NaN)")
    
    if np.any(np.isinf(y)):
        raise ValueError("Input data contains infinite values")
    
    if len(y) < 20:
        raise ValueError("Time series must have at least 20 observations")
    
    return y


def _get_fourier_terms(T: int, k: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Fourier terms sin(2πkt/T) and cos(2πkt/T).
    
    Following Li & Zheng (2018) equation (2):
    α(t) ≅ α_0 + α_k * sin(2πkt/T) + β_k * cos(2πkt/T)
    
    Parameters
    ----------
    T : int
        Sample size (number of observations).
    k : int
        Fourier frequency component.
        
    Returns
    -------
    sin_k : np.ndarray
        Sine Fourier terms of shape (T,).
    cos_k : np.ndarray
        Cosine Fourier terms of shape (T,).
    """
    t = np.arange(1, T + 1)
    sin_k = np.sin(2 * np.pi * k * t / T)
    cos_k = np.cos(2 * np.pi * k * t / T)
    return sin_k, cos_k


def _get_deterministic_components(y: np.ndarray) -> Tuple[int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute deterministic components for the regression.
    
    Parameters
    ----------
    y : np.ndarray
        Input time series.
        
    Returns
    -------
    T : int
        Sample size.
    dy : np.ndarray
        First difference of y.
    y_lag : np.ndarray
        Lagged y (y_{t-1}).
    constant : np.ndarray
        Vector of ones.
    trend : np.ndarray
        Linear time trend.
    """
    T = len(y)
    dy = np.diff(y)
    y_lag = y[:-1]
    constant = np.ones(T)
    trend = np.arange(1, T + 1)
    
    return T, dy, y_lag, constant, trend


def _estimate_sparsity(residuals: np.ndarray, tau: float, method: str = 'bofinger') -> float:
    """
    Estimate the sparsity function f(F^{-1}(τ)) using kernel density estimation.
    
    This follows Bofinger (1975) bandwidth choice as mentioned in Li & Zheng (2018).
    
    Parameters
    ----------
    residuals : np.ndarray
        Regression residuals.
    tau : float
        Quantile level.
    method : str, optional
        Bandwidth method: 'bofinger' (default), 'hall_sheather', or 'chamberlain'.
        
    Returns
    -------
    f_inv : float
        Estimated sparsity 1/f(F^{-1}(τ)).
    """
    n = len(residuals)
    
    # Bandwidth selection following Bofinger (1975)
    if method == 'bofinger':
        # Bofinger bandwidth: h = n^{-1/5} * [(4.5 * φ(Φ^{-1}(τ))^4) / (2 * Φ^{-1}(τ)^2 + 1)^2]^{1/5}
        z_tau = stats.norm.ppf(tau)
        phi_z = stats.norm.pdf(z_tau)
        
        if abs(z_tau) < 1e-10:
            z_tau = 1e-10
            
        h = n ** (-1/5) * ((4.5 * phi_z**4) / (2 * z_tau**2 + 1)**2) ** (1/5)
    elif method == 'hall_sheather':
        # Hall-Sheather bandwidth
        z_alpha = stats.norm.ppf(1 - 0.05/2)
        z_tau = stats.norm.ppf(tau)
        phi_z = stats.norm.pdf(z_tau)
        h = n ** (-1/3) * z_alpha ** (2/3) * ((1.5 * phi_z**2) / (2 * z_tau**2 + 1)) ** (1/3)
    else:
        # Chamberlain bandwidth
        h = stats.norm.ppf(tau + 0.05) - stats.norm.ppf(tau - 0.05)
    
    h = max(h, 0.01)  # Ensure positive bandwidth
    h = min(h, 0.5)   # Cap bandwidth
    
    # Estimate density at the τ-th quantile
    sorted_resid = np.sort(residuals)
    n_resid = len(sorted_resid)
    
    # Find indices for bandwidth
    lower_idx = max(0, int(np.floor((tau - h) * n_resid)))
    upper_idx = min(n_resid - 1, int(np.ceil((tau + h) * n_resid)))
    
    if upper_idx <= lower_idx:
        upper_idx = lower_idx + 1
    
    # Difference quotient estimator
    x_upper = sorted_resid[upper_idx]
    x_lower = sorted_resid[lower_idx]
    
    if abs(x_upper - x_lower) < 1e-10:
        f_hat = 1e-10
    else:
        f_hat = (2 * h) / (x_upper - x_lower)
    
    f_inv = 1.0 / max(f_hat, 1e-10)
    
    return f_inv


def _quantile_regression(y: np.ndarray, X: np.ndarray, tau: float, 
                         max_iter: int = 1000, tol: float = 1e-8) -> np.ndarray:
    """
    Estimate quantile regression coefficients using iteratively reweighted least squares.
    
    Solves: argmin_θ Σ ρ_τ(y_t - θ'z_t) where ρ_τ(u) = u(τ - I(u < 0))
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    X : np.ndarray
        Design matrix.
    tau : float
        Quantile level (0 < tau < 1).
    max_iter : int, optional
        Maximum number of iterations.
    tol : float, optional
        Convergence tolerance.
        
    Returns
    -------
    beta : np.ndarray
        Estimated coefficients.
    """
    n, p = X.shape
    
    # Initial estimate using OLS
    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
    except np.linalg.LinAlgError:
        beta = np.zeros(p)
    
    # IRLS algorithm
    for iteration in range(max_iter):
        beta_old = beta.copy()
        
        # Compute residuals
        residuals = y - X @ beta
        
        # Compute weights for quantile regression
        # w_i = τ/|r_i| if r_i > 0, else (1-τ)/|r_i|
        weights = np.where(residuals >= 0, tau, 1 - tau)
        abs_residuals = np.abs(residuals)
        abs_residuals = np.maximum(abs_residuals, 1e-10)  # Avoid division by zero
        weights = weights / abs_residuals
        
        # Weighted least squares
        W = np.diag(weights)
        try:
            XtWX = X.T @ W @ X
            XtWy = X.T @ W @ y
            
            # Add small regularization for numerical stability
            XtWX += 1e-10 * np.eye(p)
            
            beta = np.linalg.solve(XtWX, XtWy)
        except np.linalg.LinAlgError:
            break
        
        # Check convergence
        if np.max(np.abs(beta - beta_old)) < tol:
            break
    
    return beta


def _compute_tn_statistic(y: np.ndarray, y_lag: np.ndarray, X: np.ndarray, 
                          rho_tau: float, tau: float, f_inv: float) -> float:
    """
    Compute the t_n statistic for the quantile Fourier ADF test.
    
    Following Li & Zheng (2018) equation (8):
    t_f(τ) = [f̂(F^{-1}(τ)) / √(τ(1-τ))] * (Y'_{-1} M_x Y_{-1})^{1/2} * (φ̂ - 1)
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    y_lag : np.ndarray
        Lagged dependent variable y_{t-1}.
    X : np.ndarray
        Full design matrix (including y_lag).
    rho_tau : float
        Estimated AR coefficient at quantile tau.
    tau : float
        Quantile level.
    f_inv : float
        Estimated sparsity function.
        
    Returns
    -------
    tn : float
        The t_n test statistic.
    """
    n = len(y)
    
    # Extract deterministic regressors (excluding y_lag)
    # X structure: [y_lag, dy_lags (if any), sin, cos, (trend if model 2)]
    X_det = X[:, 1:]  # Remove y_lag column
    
    # Project y_lag onto the space orthogonal to X_det (M_x operator)
    # M_x = I - X_det(X_det'X_det)^{-1}X_det'
    try:
        XtX_inv = np.linalg.inv(X_det.T @ X_det + 1e-10 * np.eye(X_det.shape[1]))
        projection = X_det @ XtX_inv @ X_det.T
        M_x = np.eye(n) - projection
    except np.linalg.LinAlgError:
        M_x = np.eye(n)
    
    # Compute Y'_{-1} M_x Y_{-1}
    y_lag_M = M_x @ y_lag
    y_lag_M_y_lag = y_lag.T @ M_x @ y_lag
    
    # Compute t_n statistic following equation (8)
    if y_lag_M_y_lag <= 0:
        y_lag_M_y_lag = 1e-10
    
    denominator = np.sqrt(tau * (1 - tau))
    if denominator < 1e-10:
        denominator = 1e-10
    
    tn = (1.0 / f_inv) * np.sqrt(y_lag_M_y_lag) * (rho_tau - 1) / denominator
    
    return tn


def qr_fourier_adf(y: Union[np.ndarray, pd.Series], 
                   model: int = 1, 
                   tau: float = 0.5, 
                   pmax: int = 8, 
                   k: int = 3,
                   print_results: bool = True) -> Dict:
    """
    Quantile Fourier ADF Unit Root Test.
    
    This function implements the quantile autoregression unit root test with
    Fourier approximation for smooth structural changes, as proposed by
    Li & Zheng (2018).
    
    The null hypothesis is H_0: φ = 1 (unit root).
    
    Parameters
    ----------
    y : array_like
        Time series data (1-dimensional).
    model : int, optional
        Deterministic specification:
        - 1: Model with constant only (default)
        - 2: Model with constant and trend
    tau : float, optional
        Quantile level (0 < tau < 1). Default is 0.5 (median).
    pmax : int, optional
        Number of lags for Δy. Default is 8.
    k : int, optional
        Number of Fourier frequency component (1 ≤ k ≤ 5). Default is 3.
    print_results : bool, optional
        If True, print formatted results. Default is True.
        
    Returns
    -------
    results : dict
        Dictionary containing:
        - 'tn': The t_n test statistic
        - 'rho_tau': Estimated AR coefficient at quantile tau
        - 'tau': The quantile level used
        - 'model': Model specification (1 or 2)
        - 'k': Fourier frequency used
        - 'pmax': Number of lags used
        - 'n': Effective sample size
        
    References
    ----------
    Li, H., & Zheng, C. (2018). Unit root quantile autoregression testing with
    smooth structural changes. Finance Research Letters, 25, 83-89.
    
    Examples
    --------
    >>> import numpy as np
    >>> from qfadf import qr_fourier_adf
    >>> np.random.seed(42)
    >>> y = np.cumsum(np.random.randn(200))  # Random walk
    >>> results = qr_fourier_adf(y, model=1, tau=0.5)
    """
    # Validate inputs
    if not 0 < tau < 1:
        raise ValueError("tau must be between 0 and 1 (exclusive)")
    
    if model not in [1, 2]:
        raise ValueError("model must be 1 (constant) or 2 (constant + trend)")
    
    if k < 1 or k > 5:
        raise ValueError("k (Fourier frequency) must be between 1 and 5")
    
    if pmax < 0:
        raise ValueError("pmax must be non-negative")
    
    # Prepare data
    y = _check_data(y)
    
    # Get deterministic components
    T_full, dy, y_lag_full, constant, trend = _get_deterministic_components(y)
    
    # Trim for lags
    # We lose pmax+1 observations: 1 for differencing, pmax for lagged differences
    y_trimmed = y[pmax + 1:]
    y_lag = y_lag_full[pmax:]  # This is y_{t-1}
    
    # Update effective sample size
    T = len(y_trimmed)
    
    if T < 20:
        raise ValueError(f"Effective sample size ({T}) too small after trimming for lags")
    
    # Construct design matrix X
    # Following GAUSS code: x = y1 ~ dyl ~ sink ~ cosk (~ dt for model 2)
    
    # Start with lagged y (ỹ_{t-1} in the paper notation)
    X = y_lag.reshape(-1, 1)
    
    # Add lagged differences if pmax > 0
    if pmax > 0:
        dy_lags = np.zeros((T, pmax))
        for j in range(1, pmax + 1):
            # lagn(dy, j) shifted appropriately
            dy_lags[:, j-1] = dy[pmax - j:pmax - j + T]
        X = np.hstack([X, dy_lags])
    
    # Get Fourier terms for the trimmed sample
    sin_k, cos_k = _get_fourier_terms(T, k)
    X = np.hstack([X, sin_k.reshape(-1, 1), cos_k.reshape(-1, 1)])
    
    # Add trend if model 2
    if model == 2:
        trend_trimmed = np.arange(pmax + 2, pmax + 2 + T)
        X = np.hstack([X, trend_trimmed.reshape(-1, 1)])
    
    # Quantile regression estimation
    beta = _quantile_regression(y_trimmed, X, tau)
    
    # Extract rho(tau) - the AR coefficient at quantile tau
    rho_tau = beta[0]
    
    # Compute residuals
    residuals = y_trimmed - X @ beta
    
    # Estimate sparsity function
    f_inv = _estimate_sparsity(residuals, tau, method='bofinger')
    
    # Compute t_n statistic
    tn = _compute_tn_statistic(y_trimmed, y_lag, X, rho_tau, tau, f_inv)
    
    # Prepare results
    results = {
        'tn': tn,
        'rho_tau': rho_tau,
        'tau': tau,
        'model': model,
        'k': k,
        'pmax': pmax,
        'n': T,
        'f_inv': f_inv,
        'coefficients': beta
    }
    
    if print_results:
        _print_results(results)
    
    return results


def _print_results(results: Dict) -> None:
    """
    Print formatted test results suitable for publication.
    
    Parameters
    ----------
    results : dict
        Dictionary containing test results.
    """
    model_desc = "Constant" if results['model'] == 1 else "Constant + Trend"
    
    print("\n" + "=" * 70)
    print("         QUANTILE FOURIER ADF UNIT ROOT TEST")
    print("         Li & Zheng (2018, Finance Research Letters)")
    print("=" * 70)
    print(f"\n  Model:                {model_desc}")
    print(f"  Fourier frequency k:  {results['k']}")
    print(f"  Lags (pmax):          {results['pmax']}")
    print(f"  Sample size:          {results['n']}")
    print("\n" + "-" * 70)
    print("  Test Results:")
    print("-" * 70)
    print(f"  Quantile (τ):         {results['tau']:.3f}")
    print(f"  ρ(τ):                 {results['rho_tau']:.6f}")
    print(f"  t_f(τ) statistic:     {results['tn']:.4f}")
    print("-" * 70)
    print("\n  H0: Unit root (φ = 1)")
    print("  H1: Stationary (φ < 1)")
    print("\n  Note: Use bootstrap critical values for inference.")
    print("        Reject H0 if t_f(τ) < critical value.")
    print("=" * 70 + "\n")


def estimate_optimal_k(y: Union[np.ndarray, pd.Series], 
                       model: int = 1,
                       tau: float = 0.5,
                       pmax: int = 8,
                       k_max: int = 5) -> int:
    """
    Estimate optimal Fourier frequency k by minimizing residual sum of squares.
    
    Following Enders & Lee (2012a), this function selects k that minimizes
    the residual sum of squares across k = 1, ..., k_max.
    
    Parameters
    ----------
    y : array_like
        Time series data.
    model : int, optional
        Model specification (1 or 2). Default is 1.
    tau : float, optional
        Quantile level. Default is 0.5.
    pmax : int, optional
        Number of lags. Default is 8.
    k_max : int, optional
        Maximum frequency to consider. Default is 5.
        
    Returns
    -------
    k_opt : int
        Optimal Fourier frequency.
    """
    y = _check_data(y)
    
    rss_values = []
    
    for k in range(1, k_max + 1):
        try:
            results = qr_fourier_adf(y, model=model, tau=tau, pmax=pmax, k=k, 
                                     print_results=False)
            
            # Compute RSS
            T_full, dy, y_lag_full, constant, trend = _get_deterministic_components(y)
            y_trimmed = y[pmax + 1:]
            y_lag = y_lag_full[pmax:]
            T = len(y_trimmed)
            
            X = y_lag.reshape(-1, 1)
            if pmax > 0:
                dy_lags = np.zeros((T, pmax))
                for j in range(1, pmax + 1):
                    dy_lags[:, j-1] = dy[pmax - j:pmax - j + T]
                X = np.hstack([X, dy_lags])
            
            sin_k, cos_k = _get_fourier_terms(T, k)
            X = np.hstack([X, sin_k.reshape(-1, 1), cos_k.reshape(-1, 1)])
            
            if model == 2:
                trend_trimmed = np.arange(pmax + 2, pmax + 2 + T)
                X = np.hstack([X, trend_trimmed.reshape(-1, 1)])
            
            residuals = y_trimmed - X @ results['coefficients']
            rss = np.sum(residuals ** 2)
            rss_values.append((k, rss))
            
        except Exception:
            rss_values.append((k, np.inf))
    
    # Select k with minimum RSS
    k_opt = min(rss_values, key=lambda x: x[1])[0]
    
    return k_opt


def qks_qcm_statistics(y: Union[np.ndarray, pd.Series],
                       model: int = 1,
                       pmax: int = 8,
                       k: int = 3,
                       tau_range: Tuple[float, float] = (0.1, 0.9),
                       n_quantiles: int = 19) -> Dict:
    """
    Compute QKS_f and QCM_f statistics over a range of quantiles.
    
    Following Li & Zheng (2018) Section 3.3:
    - QKS_f = sup_{τ∈T} |t_f(τ)|
    - QCM_f = ∫_{τ∈T} t_f(τ)² dτ
    
    Parameters
    ----------
    y : array_like
        Time series data.
    model : int, optional
        Model specification (1 or 2). Default is 1.
    pmax : int, optional
        Number of lags. Default is 8.
    k : int, optional
        Fourier frequency. Default is 3.
    tau_range : tuple, optional
        Range of quantiles (τ_0, 1-τ_0). Default is (0.1, 0.9).
    n_quantiles : int, optional
        Number of quantile points. Default is 19.
        
    Returns
    -------
    results : dict
        Dictionary containing:
        - 'QKS_f': Quantile Kolmogorov-Smirnov statistic
        - 'QCM_f': Quantile Cramér-von Mises statistic
        - 'tau_values': Array of quantile levels
        - 't_f_values': Array of t_f statistics at each quantile
        - 'rho_values': Array of ρ(τ) at each quantile
    """
    tau_values = np.linspace(tau_range[0], tau_range[1], n_quantiles)
    t_f_values = np.zeros(n_quantiles)
    rho_values = np.zeros(n_quantiles)
    
    for i, tau in enumerate(tau_values):
        try:
            result = qr_fourier_adf(y, model=model, tau=tau, pmax=pmax, k=k, 
                                    print_results=False)
            t_f_values[i] = result['tn']
            rho_values[i] = result['rho_tau']
        except Exception as e:
            warnings.warn(f"Error at tau={tau:.3f}: {str(e)}")
            t_f_values[i] = np.nan
            rho_values[i] = np.nan
    
    # Compute QKS_f = sup |t_f(τ)|
    QKS_f = np.nanmax(np.abs(t_f_values))
    
    # Compute QCM_f = ∫ t_f(τ)² dτ using numerical integration
    # Using trapezoidal rule
    valid_idx = ~np.isnan(t_f_values)
    if np.sum(valid_idx) >= 2:
        QCM_f = np.trapz(t_f_values[valid_idx]**2, tau_values[valid_idx])
    else:
        QCM_f = np.nan
    
    results = {
        'QKS_f': QKS_f,
        'QCM_f': QCM_f,
        'tau_values': tau_values,
        't_f_values': t_f_values,
        'rho_values': rho_values,
        'model': model,
        'k': k,
        'pmax': pmax
    }
    
    return results
