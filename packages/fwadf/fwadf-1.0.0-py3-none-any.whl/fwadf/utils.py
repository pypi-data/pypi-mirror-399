"""
Utility Functions for FWADF/WADF Tests

Contains helper functions for lag matrix construction, information criteria
calculation, OLS estimation, and other utility operations.
"""

import numpy as np
from typing import Tuple, Optional, Union, Literal


def lag(data: np.ndarray, k: int = 1) -> np.ndarray:
    """
    Create a lagged version of the input array.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series (1D array).
    k : int
        Number of lags (default: 1).
    
    Returns
    -------
    np.ndarray
        Lagged array with NaN for initial values.
    
    Examples
    --------
    >>> data = np.array([1, 2, 3, 4, 5])
    >>> lag(data, 1)
    array([nan, 1., 2., 3., 4.])
    """
    data = np.asarray(data).flatten()
    n = len(data)
    
    if k >= n:
        raise ValueError(f"Lag {k} must be less than data length {n}.")
    
    lagged = np.empty(n)
    lagged[:k] = np.nan
    lagged[k:] = data[:-k] if k > 0 else data
    
    return lagged


def diff(data: np.ndarray, d: int = 1) -> np.ndarray:
    """
    Compute the d-th difference of the input array.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series.
    d : int
        Order of differencing (default: 1).
    
    Returns
    -------
    np.ndarray
        Differenced series (length reduced by d).
    """
    data = np.asarray(data).flatten()
    result = data.copy()
    
    for _ in range(d):
        result = np.diff(result)
    
    return result


def create_lag_matrix(data: np.ndarray, max_lags: int) -> np.ndarray:
    """
    Create a matrix of lagged values.
    
    Parameters
    ----------
    data : np.ndarray
        Input time series.
    max_lags : int
        Maximum number of lags to include.
    
    Returns
    -------
    np.ndarray
        Matrix with columns [lag1, lag2, ..., lag_max_lags].
        Shape is (n, max_lags).
    """
    data = np.asarray(data).flatten()
    n = len(data)
    
    if max_lags <= 0:
        return np.empty((n, 0))
    
    lag_matrix = np.zeros((n, max_lags))
    
    for j in range(1, max_lags + 1):
        lag_matrix[j:, j - 1] = data[:-j]
        lag_matrix[:j, j - 1] = np.nan
    
    return lag_matrix


def trimr(data: np.ndarray, front: int, back: int) -> np.ndarray:
    """
    Trim rows from front and back of array (GAUSS-compatible function).
    
    Parameters
    ----------
    data : np.ndarray
        Input array.
    front : int
        Number of rows to remove from the beginning.
    back : int
        Number of rows to remove from the end.
    
    Returns
    -------
    np.ndarray
        Trimmed array.
    """
    data = np.asarray(data)
    
    if data.ndim == 1:
        if back == 0:
            return data[front:]
        else:
            return data[front:-back] if back > 0 else data[front:]
    else:
        if back == 0:
            return data[front:, :]
        else:
            return data[front:-back, :] if back > 0 else data[front:, :]


def ols_estimate(y: np.ndarray, X: np.ndarray) -> dict:
    """
    Perform OLS estimation with detailed statistics.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (n x 1).
    X : np.ndarray
        Independent variables (n x k).
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'beta': Coefficient estimates
        - 'residuals': OLS residuals
        - 'ssr': Sum of squared residuals
        - 's2': Estimated variance of residuals
        - 'se': Standard errors of coefficients
        - 't_stats': t-statistics for coefficients
        - 'inv_xx': Inverse of X'X matrix
        - 'n': Number of observations
        - 'k': Number of regressors
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    n, k = X.shape
    
    # OLS estimation: beta = (X'X)^(-1) X'y
    try:
        inv_xx = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        # Use pseudo-inverse for singular matrices
        inv_xx = np.linalg.pinv(X.T @ X)
    
    beta = inv_xx @ X.T @ y
    
    # Residuals
    residuals = y - X @ beta
    
    # Sum of squared residuals
    ssr = residuals.T @ residuals
    
    # Estimated variance (degrees of freedom adjusted)
    s2 = ssr / (n - k) if n > k else ssr / n
    
    # Standard errors
    se = np.sqrt(np.diag(s2 * inv_xx))
    
    # t-statistics
    t_stats = beta / se
    
    return {
        'beta': beta,
        'residuals': residuals,
        'ssr': float(ssr),
        's2': float(s2),
        'se': se,
        't_stats': t_stats,
        'inv_xx': inv_xx,
        'n': n,
        'k': k
    }


def aic(residuals: np.ndarray, k: int) -> float:
    """
    Calculate Akaike Information Criterion (AIC).
    
    Following the formula used in the original GAUSS code:
        AIC = ln(SSR/n) + 2*(k + 2)/n
    
    Parameters
    ----------
    residuals : np.ndarray
        OLS residuals.
    k : int
        Number of parameters in the model.
    
    Returns
    -------
    float
        AIC value.
    """
    residuals = np.asarray(residuals).flatten()
    n = len(residuals)
    ssr = residuals.T @ residuals
    
    return np.log(ssr / n) + 2 * (k + 2) / n


def bic(residuals: np.ndarray, k: int) -> float:
    """
    Calculate Bayesian Information Criterion (BIC/SIC).
    
    Following the formula used in the original GAUSS code:
        BIC = ln(SSR/n) + (k + 2) * ln(n) / n
    
    Parameters
    ----------
    residuals : np.ndarray
        OLS residuals.
    k : int
        Number of parameters in the model.
    
    Returns
    -------
    float
        BIC value.
    """
    residuals = np.asarray(residuals).flatten()
    n = len(residuals)
    ssr = residuals.T @ residuals
    
    return np.log(ssr / n) + (k + 2) * np.log(n) / n


def select_lag_ic(y: np.ndarray, X_base: np.ndarray, 
                  dy_lags: np.ndarray, max_lags: int,
                  criterion: Literal['aic', 'bic'] = 'bic') -> Tuple[int, float]:
    """
    Select optimal lag length using information criterion.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable.
    X_base : np.ndarray
        Base regressors (without lagged differences).
    dy_lags : np.ndarray
        Matrix of lagged first differences.
    max_lags : int
        Maximum lag length to consider.
    criterion : str
        Information criterion ('aic' or 'bic').
    
    Returns
    -------
    optimal_lag : int
        Selected optimal lag length.
    ic_value : float
        Information criterion value at optimal lag.
    """
    ic_func = aic if criterion.lower() == 'aic' else bic
    
    ic_values = np.full(max_lags + 1, np.inf)
    
    for p in range(max_lags + 1):
        if p == 0:
            X = X_base
        else:
            X = np.column_stack([X_base, dy_lags[:, :p]])
        
        # Remove NaN rows
        valid_idx = ~(np.any(np.isnan(X), axis=1) | np.isnan(y))
        y_valid = y[valid_idx]
        X_valid = X[valid_idx, :]
        
        if len(y_valid) < X_valid.shape[1] + 1:
            continue
        
        result = ols_estimate(y_valid, X_valid)
        ic_values[p] = ic_func(result['residuals'], X_valid.shape[1])
    
    optimal_lag = np.argmin(ic_values)
    return int(optimal_lag), float(ic_values[optimal_lag])


def calculate_max_lag(T: int, method: str = 'schwert') -> int:
    """
    Calculate maximum lag length based on sample size.
    
    Parameters
    ----------
    T : int
        Sample size.
    method : str
        Method to use:
        - 'schwert': int(12 * (T/100)^(1/4)) - Schwert (1989)
        - 'sephton': int(0.75 * T^(1/3)) - Used in Sephton (2024)
        - 'ng_perron': int(4 * (T/100)^(2/9)) - Ng & Perron (2001)
    
    Returns
    -------
    int
        Maximum lag length.
    
    References
    ----------
    Schwert, G.W. (1989). Tests for unit roots: A Monte Carlo investigation.
        Journal of Business & Economic Statistics, 7(2), 147-159.
    Sephton, P.S. (2024). Computational Economics, 64, 693-705.
    """
    method = method.lower()
    
    if method == 'schwert':
        return int(12 * (T / 100) ** 0.25)
    elif method == 'sephton':
        return int(0.75 * T ** (1/3))
    elif method == 'ng_perron':
        return int(4 * (T / 100) ** (2/9))
    else:
        raise ValueError(f"Unknown method: {method}. Use 'schwert', 'sephton', or 'ng_perron'.")


def generate_unit_root_process(T: int, burn: int = 100, 
                               seed: Optional[int] = None) -> np.ndarray:
    """
    Generate a unit root process (random walk) for simulation.
    
    y_t = y_{t-1} + epsilon_t, where epsilon_t ~ N(0, 1)
    
    Parameters
    ----------
    T : int
        Sample size.
    burn : int
        Burn-in period to discard.
    seed : int, optional
        Random seed for reproducibility.
    
    Returns
    -------
    np.ndarray
        Unit root process of length T.
    """
    if seed is not None:
        np.random.seed(seed)
    
    total_length = T + burn
    epsilon = np.random.standard_normal(total_length)
    y = np.cumsum(epsilon)
    
    return y[burn:]


def create_fourier_term(T: int, k: float) -> np.ndarray:
    """
    Create Fourier sine term for the FWADF test.
    
    sin(2 * pi * k * t / T)
    
    Parameters
    ----------
    T : int
        Sample size.
    k : float
        Fourier frequency.
    
    Returns
    -------
    np.ndarray
        Fourier sine term of length T.
    
    Notes
    -----
    Following Enders & Lee (2012), only the sine term is used
    for the unit root test.
    """
    t = np.arange(1, T + 1)
    return np.sin(2 * np.pi * k * t / T)


def create_deterministic_terms(T: int, model: int, 
                              k: Optional[float] = None) -> np.ndarray:
    """
    Create deterministic terms for the testing equation.
    
    Parameters
    ----------
    T : int
        Sample size.
    model : int
        Model specification:
        0: No constant
        1: Constant only
        2: Constant and trend
    k : float, optional
        Fourier frequency (if None, no Fourier term is included).
    
    Returns
    -------
    np.ndarray
        Matrix of deterministic terms.
    """
    terms = []
    
    # Constant
    if model >= 1:
        terms.append(np.ones(T))
    
    # Trend
    if model >= 2:
        terms.append(np.arange(1, T + 1))
    
    # Fourier term
    if k is not None:
        terms.append(create_fourier_term(T, k))
    
    if len(terms) == 0:
        return np.empty((T, 0))
    
    return np.column_stack(terms)


def format_test_result(test_name: str, statistic: float, 
                       pvalue: Optional[float], lag: int,
                       k: Optional[float] = None,
                       critical_values: Optional[dict] = None) -> str:
    """
    Format test results for display.
    
    Parameters
    ----------
    test_name : str
        Name of the test.
    statistic : float
        Test statistic value.
    pvalue : float, optional
        P-value.
    lag : int
        Selected lag length.
    k : float, optional
        Fourier frequency (for FWADF).
    critical_values : dict, optional
        Dictionary of critical values.
    
    Returns
    -------
    str
        Formatted output string.
    """
    lines = ["=" * 60]
    lines.append(f"{test_name}")
    lines.append("=" * 60)
    
    if k is not None:
        lines.append(f"Fourier Frequency (k):    {k:.1f}")
    lines.append(f"Lag Length:               {lag}")
    lines.append(f"Test Statistic:           {statistic:.4f}")
    
    if pvalue is not None:
        lines.append(f"P-value:                  {pvalue:.4f}")
        
        # Significance indicators
        if pvalue < 0.01:
            sig = "***"
        elif pvalue < 0.05:
            sig = "**"
        elif pvalue < 0.10:
            sig = "*"
        else:
            sig = ""
        if sig:
            lines.append(f"Significance:             {sig}")
    
    if critical_values:
        lines.append("-" * 60)
        lines.append("Critical Values:")
        for level, cv in sorted(critical_values.items()):
            lines.append(f"  {level*100:.0f}%:                     {cv:.4f}")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
