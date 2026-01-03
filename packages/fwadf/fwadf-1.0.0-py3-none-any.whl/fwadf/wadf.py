"""
Wavelet Augmented Dickey-Fuller (WADF) Unit Root Test

Implementation of the WADF unit root test following Eroglu & Soybilgen (2018).

The WADF test applies the ADF testing procedure to the low-frequency (scaling)
coefficients obtained from Haar wavelet decomposition.

References:
    Eroglu, B. & Soybilgen, B. (2018). "On the Performance of Wavelet Based 
    Unit Root Tests." Journal of Risk and Financial Management, 11(3), 47.
    
    Aydin, M. & Pata, U.K. (2020). Energy, 207, 118245.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Literal, Union, Tuple

from .wavelet import haar_scaling_coefficients
from .utils import (lag, diff, create_lag_matrix, trimr, ols_estimate,
                    aic, bic, calculate_max_lag, create_deterministic_terms)


@dataclass
class WADFResult:
    """
    Results from WADF unit root test.
    
    Attributes
    ----------
    statistic : float
        WADF test statistic (t-statistic on delta).
    pvalue : float
        Approximate p-value.
    lag : int
        Selected lag length.
    model : int
        Model specification (0: none, 1: constant, 2: constant+trend).
    ic_criterion : str
        Information criterion used for lag selection.
    sample_size : int
        Original sample size.
    wavelet_sample_size : int
        Sample size after wavelet transformation.
    critical_values : dict
        Critical values at common significance levels.
    delta : float
        Estimated coefficient on lagged level.
    se_delta : float
        Standard error of delta.
    ssr : float
        Sum of squared residuals.
    regression_results : dict
        Full OLS regression results.
    """
    statistic: float
    pvalue: float
    lag: int
    model: int
    ic_criterion: str
    sample_size: int
    wavelet_sample_size: int
    critical_values: dict
    delta: float
    se_delta: float
    ssr: float
    regression_results: dict
    
    def __repr__(self) -> str:
        model_names = {0: "No Deterministics", 
                       1: "Constant", 
                       2: "Constant and Trend"}
        
        lines = [
            "=" * 60,
            "Wavelet Augmented Dickey-Fuller (WADF) Test Results",
            "=" * 60,
            f"Model:                    {model_names.get(self.model, 'Unknown')}",
            f"Original Sample Size:     {self.sample_size}",
            f"Wavelet Sample Size:      {self.wavelet_sample_size}",
            f"Lag Selection:            {self.ic_criterion.upper()}",
            f"Selected Lag Length:      {self.lag}",
            "-" * 60,
            f"Test Statistic:           {self.statistic:.4f}",
            f"P-value:                  {self.pvalue:.4f}",
            "-" * 60,
            "Critical Values:"
        ]
        
        for level, cv in sorted(self.critical_values.items()):
            lines.append(f"  {level*100:.0f}%:                     {cv:.4f}")
        
        lines.append("-" * 60)
        
        # Conclusion
        if self.pvalue < 0.01:
            conclusion = "Reject H0 at 1% level (Stationary)"
        elif self.pvalue < 0.05:
            conclusion = "Reject H0 at 5% level (Stationary)"
        elif self.pvalue < 0.10:
            conclusion = "Reject H0 at 10% level (Stationary)"
        else:
            conclusion = "Cannot reject H0 (Unit Root)"
        
        lines.append(f"Conclusion:               {conclusion}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def summary(self) -> str:
        """Return formatted summary string."""
        return self.__repr__()


def wadf_test(
    data: np.ndarray,
    model: int = 1,
    max_lag: Optional[int] = None,
    ic: Literal['aic', 'bic'] = 'bic',
    verbose: bool = True
) -> WADFResult:
    """
    Perform the Wavelet Augmented Dickey-Fuller (WADF) unit root test.
    
    The WADF test applies standard ADF testing to the low-frequency (scaling)
    coefficients obtained from Haar wavelet decomposition. This concentrates
    the test on the unit root behavior, improving power.
    
    Test Equation:
        ΔV_t = δ*V_{t-1} + Σ(ρ_j * ΔV_{t-j}) + deterministics + ε_t
    
    where V_t are the Haar scaling coefficients.
    
    Null Hypothesis: δ = 0 (series has unit root)
    Alternative Hypothesis: δ < 0 (series is stationary)
    
    Parameters
    ----------
    data : np.ndarray
        Input time series data (1-dimensional array).
    model : int, optional
        Model specification (default: 1):
        - 0: No deterministic terms
        - 1: Constant only
        - 2: Constant and linear trend
    max_lag : int, optional
        Maximum lag length to consider. If None, uses int(0.75*T^(1/3))
        following Sephton (2024).
    ic : str, optional
        Information criterion for lag selection (default: 'bic'):
        - 'aic': Akaike Information Criterion
        - 'bic': Bayesian/Schwarz Information Criterion
    verbose : bool, optional
        If True, print results summary (default: True).
    
    Returns
    -------
    WADFResult
        Object containing test results, including:
        - statistic: WADF test statistic
        - pvalue: Approximate p-value
        - lag: Selected lag length
        - critical_values: Critical values at 1%, 5%, 10%
    
    Examples
    --------
    >>> import numpy as np
    >>> from fwadf import wadf_test
    >>> # Generate random walk
    >>> np.random.seed(42)
    >>> data = np.cumsum(np.random.randn(200))
    >>> result = wadf_test(data, model=1)
    >>> print(f"Test statistic: {result.statistic:.4f}")
    >>> print(f"P-value: {result.pvalue:.4f}")
    
    Notes
    -----
    The WADF test is a lower-tailed test. Reject the null hypothesis of
    unit root when the test statistic is sufficiently negative
    (more negative than the critical value).
    
    References
    ----------
    Eroglu, B. & Soybilgen, B. (2018). Journal of Risk and Financial Management.
    """
    # Validate input
    data = np.asarray(data).flatten()
    original_n = len(data)
    
    if original_n < 20:
        raise ValueError("Input data must have at least 20 observations.")
    
    if model not in [0, 1, 2]:
        raise ValueError("Model must be 0 (none), 1 (constant), or 2 (constant+trend).")
    
    # Apply Haar wavelet transformation to get scaling coefficients
    V = haar_scaling_coefficients(data)
    T = len(V)
    
    if T < 10:
        raise ValueError("Wavelet-transformed series too short. Need more observations.")
    
    # Set maximum lag if not specified
    if max_lag is None:
        max_lag = calculate_max_lag(T, method='sephton')
    
    max_lag = min(max_lag, T // 4)  # Ensure we have enough observations
    
    # Prepare data for ADF regression
    # ΔV_t = δ*V_{t-1} + Σ(ρ_j * ΔV_{t-j}) + deterministics + ε_t
    
    # First difference of V
    dV = diff(V)
    
    # Lagged level (V_{t-1})
    V_lag1 = V[:-1]  # V_{t-1} aligned with ΔV_t
    
    # Lagged differences for augmentation
    dV_lags = np.zeros((len(dV), max_lag))
    for j in range(1, max_lag + 1):
        dV_lags[j:, j-1] = dV[:-j]
        dV_lags[:j, j-1] = np.nan
    
    # Trim to align all series
    # We need to remove (p+1) observations from the start for p lags
    
    # Information criterion values for each lag
    ic_func = aic if ic.lower() == 'aic' else bic
    ic_values = np.full(max_lag + 1, np.inf)
    test_stats = np.zeros(max_lag + 1)
    ssr_values = np.zeros(max_lag + 1)
    results_by_lag = {}
    
    for p in range(max_lag + 1):
        # Trim data
        start_idx = p + 1
        
        dep = dV[start_idx:]
        V_lag1_trimmed = V_lag1[start_idx:]
        
        # Build regressor matrix
        # Order: V_{t-1}, deterministics, lagged differences
        if model == 0:
            X = V_lag1_trimmed.reshape(-1, 1)
        elif model == 1:
            ones = np.ones(len(dep))
            X = np.column_stack([V_lag1_trimmed, ones])
        else:  # model == 2
            ones = np.ones(len(dep))
            trend = np.arange(1, len(dep) + 1)
            X = np.column_stack([V_lag1_trimmed, ones, trend])
        
        # Add lagged differences if p > 0
        if p > 0:
            ldy = dV_lags[start_idx:, :p]
            X = np.column_stack([X, ldy])
        
        # Check for valid observations
        valid_idx = ~np.any(np.isnan(X), axis=1)
        if np.sum(valid_idx) < X.shape[1] + 1:
            continue
        
        dep_valid = dep[valid_idx]
        X_valid = X[valid_idx, :]
        
        # OLS estimation
        result = ols_estimate(dep_valid, X_valid)
        
        # Store results
        test_stats[p] = result['t_stats'][0]  # t-stat on V_{t-1}
        ssr_values[p] = result['ssr']
        ic_values[p] = ic_func(result['residuals'], X_valid.shape[1])
        results_by_lag[p] = result
    
    # Select optimal lag
    optimal_lag = int(np.argmin(ic_values))
    
    # Get results at optimal lag
    final_result = results_by_lag[optimal_lag]
    test_statistic = test_stats[optimal_lag]
    ssr = ssr_values[optimal_lag]
    
    # Get critical values and p-value
    from .critical_values import get_wadf_critical_values, get_wadf_pvalue
    
    critical_values = get_wadf_critical_values(T, optimal_lag, model)
    pvalue = get_wadf_pvalue(test_statistic, T, optimal_lag, model)
    
    # Create result object
    result = WADFResult(
        statistic=float(test_statistic),
        pvalue=float(pvalue),
        lag=optimal_lag,
        model=model,
        ic_criterion=ic,
        sample_size=original_n,
        wavelet_sample_size=T,
        critical_values=critical_values,
        delta=float(final_result['beta'][0]),
        se_delta=float(final_result['se'][0]),
        ssr=float(ssr),
        regression_results=final_result
    )
    
    if verbose:
        print(result)
    
    return result


def _wadf_statistic_fixed_lag(V: np.ndarray, lag: int, model: int) -> Tuple[float, dict]:
    """
    Calculate WADF statistic for a fixed lag length.
    
    This is an internal function used for simulation.
    
    Parameters
    ----------
    V : np.ndarray
        Scaling coefficients from wavelet transform.
    lag : int
        Fixed lag length.
    model : int
        Model specification.
    
    Returns
    -------
    test_stat : float
        WADF test statistic.
    result : dict
        OLS regression results.
    """
    T = len(V)
    
    # First difference
    dV = diff(V)
    
    # Lagged level
    V_lag1 = V[:-1]
    
    # Build lagged differences
    start_idx = lag + 1
    
    dep = dV[start_idx:]
    V_lag1_trimmed = V_lag1[start_idx:]
    
    # Build regressor matrix
    if model == 0:
        X = V_lag1_trimmed.reshape(-1, 1)
    elif model == 1:
        ones = np.ones(len(dep))
        X = np.column_stack([V_lag1_trimmed, ones])
    else:  # model == 2
        ones = np.ones(len(dep))
        trend = np.arange(1, len(dep) + 1)
        X = np.column_stack([V_lag1_trimmed, ones, trend])
    
    # Add lagged differences
    if lag > 0:
        dV_lags = np.zeros((len(dV), lag))
        for j in range(1, lag + 1):
            dV_lags[j:, j-1] = dV[:-j]
            dV_lags[:j, j-1] = np.nan
        
        ldy = dV_lags[start_idx:, :lag]
        X = np.column_stack([X, ldy])
    
    # Remove NaN rows
    valid_idx = ~np.any(np.isnan(X), axis=1)
    dep_valid = dep[valid_idx]
    X_valid = X[valid_idx, :]
    
    # OLS estimation
    result = ols_estimate(dep_valid, X_valid)
    
    return float(result['t_stats'][0]), result
